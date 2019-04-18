import logging
import subprocess as sp
import time
from collections import OrderedDict

from System.Platform import Process
from System.Platform import Processor
from Instance import Instance
from System.Platform.Google import GoogleCloudHelper

class PreemptibleInstance(Instance):

    def __init__(self, name, nr_cpus, mem, disk_space, **kwargs):
        # Call super constructor
        super(PreemptibleInstance, self).__init__(name, nr_cpus, mem, disk_space, **kwargs)

        # Indicates that instance is resettable
        self.is_preemptible = True

        # Attributes for handling instance resets
        self.max_resets = kwargs.pop("max_resets", 6)
        self.reset_count = 0

        # Stack for determining costs across resets
        self.reset_history = []

    def recreate(self):
        if self.creation_resets < self.default_num_cmd_retries:
            self.creation_resets += 1
            self.stop()
            self.start()

        else:
            logging.debug("(%s) Instance successfully created but "
                          "never became available after %s resets!" %
                          (self.name, self.default_num_cmd_retries))

            raise RuntimeError("(%s) Instance successfully created but never"
                               " became available after multiple tries!" %
                               self.name)

    def start(self):

        logging.info("(%s) Process 'start' started!" % self.name)
        cmd = self.__get_gcloud_start_cmd()

        # Run command, wait for start to complete
        self.processes["start"] = Process(cmd,
                                          cmd=cmd,
                                          stdout=sp.PIPE,
                                          stderr=sp.PIPE,
                                          shell=True,
                                          num_retries=self.default_num_cmd_retries)

        # Wait for start to complete if requested
        self.wait_process("start")

        # Wait for instance to be accessible through SSH
        logging.debug("(%s) Waiting for instance to be accessible" % self.name)
        self.wait_until_ready()

    def stop(self):

        logging.info("(%s) Process 'stop' started!" % self.name)
        cmd = self.__get_gcloud_stop_cmd()

        # Run command to stop the instances
        self.processes["stop"] = Process(cmd,
                                         cmd=cmd,
                                         stdout=sp.PIPE,
                                         stderr=sp.PIPE,
                                         shell=True,
                                         num_retries=self.default_num_cmd_retries)

        # Wait for instance to stop
        self.wait_process("stop")

    def reset(self, force_destroy=False):

        # Resetting takes place just for preemptible instances
        if not self.is_preemptible:
            return

        # Reset as standard instance if preempted b/c runtime > 24 hours
        if self.start_time is not None and time.time() - self.start_time >= (3600 * 24):
            logging.warning("(%s) Instance failed! Preemptible runtime > 24 hrs. Resetting as standard instance." % self.name)
            self.is_preemptible = False

        # Incrementing the reset count and checking if it reached the threshold
        self.reset_count += 1
        if self.reset_count >= self.max_resets:
            logging.warning("(%s) Instance failed! Instance preempted and out of reset (num resets: %s). "
                            "Resetting as standard instance." % (self.name, self.max_resets))
            # Switch to non-preemptible instance
            self.is_preemptible = False

        # Create cost history record
        prev_price = self.price
        prev_start = self.start_time

        # Restart the instance if it is preemptible and is not required to be destroyed
        if self.is_preemptible and not force_destroy:

            # Restart the instance
            self.stop()
            self.start()

            # Instance restart complete
            logging.debug("(%s) Instance restarted, continue running processes!" % self.name)

        else:
            # Recreate the instance
            self.destroy()
            self.create()

            # Instance recreation complete
            logging.debug("(%s) Instance recreated, rerunning all processes!" % self.name)

        # Add record to cost history of last run
        logging.debug("({0}) Appending to cost history: {1}, {2}, {3}".format(self.name, prev_price, prev_start,
                                                                              self.stop_time))
        self.reset_history.append((prev_price, prev_start, self.stop_time))

        # Rerun all commands if the instance is not preemptible or was previously destroyed
        if not self.is_preemptible or force_destroy:

            # Rerun all commands
            for proc_name, proc_obj in self.processes.items():

                # Skip processes that do not need to be rerun
                if proc_name in ["create", "destroy", "start", "stop"]:
                    continue

                # Skip configure_ssh specific commands if already configured
                if proc_name in ["configureSSH", "restartSSH"] and self.ssh_connections_increased:
                    continue

                # Run and wait for the command to finish
                self.run(job_name=proc_name,
                         cmd=proc_obj.get_command(),
                         docker_image=proc_obj.get_docker_image(),
                         quiet_failure=proc_obj.is_quiet())
                self.wait_process(proc_name)

            # Exit function as the rest of the code is related to an instance that was not destroyed
            return

        # Identifying which process(es) need(s) to be recalled
        commands_to_run = list()
        checkpoint_queue = list()
        add_to_checkpoint_queue = False
        fail_to_checkpoint = False
        checkpoint_commands = [i[0] for i in self.checkpoints] # create array of just the commands
        logging.debug("CHECKPOINT COMMANDS: %s" % str(checkpoint_commands))
        cleanup_output = False
        for proc_name, proc_obj in self.processes.items():

            # Skip processes that do not need to be rerun
            if proc_name in ["create", "destroy", "start", "stop"]:
                continue

            # Skip configure_ssh specific commands if already configured
            if proc_name in ["configureSSH", "restartSSH"] and self.ssh_connections_increased:
                continue

            # Skip processes that were successful and complete
            if not proc_obj.has_failed() and proc_obj.complete:
                continue

            # Adding to the checkpoint queue since we're past a checkpoint marker
            if add_to_checkpoint_queue:
                checkpoint_queue.append(proc_name)

                # if a process hasn't been completed, a process may have failed before the checkpoint
                # so we need to add all those to the list to be run
                fail_to_checkpoint = True

            else:
                commands_to_run.append(proc_name)

            # Hit a checkpoint marker, start adding to the checkpoint_queue after this process
            if proc_name in checkpoint_commands:
                if fail_to_checkpoint:
                    if cleanup_output:
                        self.__remove_wrk_out_dir()

                    # Add all the commands in the checkpoint queue to commands to run
                    commands_to_run.extend(checkpoint_queue)

                # Obtain the cleanup status of the current checkpoint
                cleanup_output = [d[1] for d in self.checkpoints if d[0] == proc_name][0]
                logging.debug("CLEAR OUTPUT IS: %s FOR process %s" % (str(cleanup_output), str(proc_name)))

                # Clear the list if we run into a new checkpoint command
                checkpoint_queue = list()
                add_to_checkpoint_queue = True

        # Still have processes in the checkpoint queue
        if len(checkpoint_queue) > 0:
            if fail_to_checkpoint:
                if cleanup_output:
                    self.__remove_wrk_out_dir()

                # Add all the commands in the checkpoint queue to commands to run
                commands_to_run.extend(checkpoint_queue)

        # Set commands that need to be rerun to rerun mode, so they are all being rerun
        for proc_to_rerun in commands_to_run:
            self.processes[proc_to_rerun].set_to_rerun()

        # Log which commands will be rerun
        logging.debug("Commands to be rerun: (%s) " % str(
            [proc_name for proc_name, proc_obj in self.processes.items() if proc_obj.needs_rerun()]))

        # Rerunning all the commands that need to be rerun
        for proc_name, proc_obj in self.processes.items():
            if proc_obj.needs_rerun():
                self.run(job_name=proc_name,
                         cmd=proc_obj.get_command(),
                         docker_image=proc_obj.get_docker_image(),
                         quiet_failure=proc_obj.is_quiet())
                self.wait_process(proc_name)

    def get_runtime(self):
        # Compute total runtime across all resets
        # Return 0 if instance hasn't started yet

        # Obtain the current instance initial runtime
        runtime = super(PreemptibleInstance, self).get_runtime()

        # Add previous costs from reset history
        for price, start, end in self.reset_history:

            # Set variables to 0 if any of them are None
            start = start or 0
            end = end or 0

            # Increment the runtime
            runtime += end - start

        return runtime

    def compute_cost(self):
        # Compute total cost across all resets
        cost = super(PreemptibleInstance, self).get_runtime() * self.price

        # Add previous costs from reset history
        for price, start, end in self.reset_history:

            # Set variables to 0 if any of them are None
            price = price or 0
            start = start or 0
            end = end or 0

            # Increment the total cost
            cost += (end - start) * price

        # The price is per hour not per second
        return cost / 3600

    def handle_failure(self, proc_name, proc_obj):

        # Determine if command can be retried
        can_retry   = False
        needs_reset = False

        logging.warning("(%s) Handling failure for proc '%s'" % (self.name, proc_name))
        logging.debug("(%s) Error code: %s" % (self.name, proc_obj.returncode))

        # Raise error if processor is locked
        if self.is_locked() and proc_name != "destroy":
            self.raise_error(proc_name, proc_obj)

        if proc_obj.returncode == 255:
            logging.warning("(%s) Waiting for 60 seconds to make sure instance wasn't preempted..." % self.name)
            time.sleep(60)

            # Resolve case when SSH server resets/closes the connection
            if "connection reset by" in proc_obj.err.lower() \
                    or "connection closed by" in proc_obj.err.lower() \
                    or "permission denied (publickey)." in proc_obj.err.lower():
                self.reset(force_destroy=True)
                return

        # Check to see if issue was caused by rate limit. If so, cool out for a random time limit
        if "Rate Limit Exceeded" in proc_obj.err:
            self.throttle_api_rate(proc_name, proc_obj)

        # Check again to make sure processor wasn't locked during sleep time
        if self.is_locked() and proc_name != "destroy":
            self.raise_error(proc_name, proc_obj)

        # Update the status from the cloud and get the new status
        self.update_status()
        curr_status = self.get_status()

        # Re-run any command (except create) if instance is up and cmd can be retried
        if curr_status == Processor.AVAILABLE:
            if proc_name == "create" and "already exists" not in proc_obj.err:
                # Sometimes create works but returns a failure
                # Just need to make sure the failure wasn't due to instance already existing
                return

            # Retry command if retries are left and command isn't 'create'
            can_retry = proc_obj.get_num_retries() > 0 and proc_name != "create"

        # Re-run destroy command if instance is creating and cmd has enough retries
        elif curr_status == Processor.CREATING:
            can_retry = proc_name == "destroy" and proc_obj.get_num_retries() > 0

        elif curr_status == Processor.DESTROYING:
            # Re-run destroy command

            # Instance is destroying itself and we know why (we killed it programmatically)
            if proc_name == "destroy" and proc_obj.get_num_retries() > 0:
                can_retry = True

            # Reset instance and re-run command if it failed and we're not sure why the instance is destroying itself (e.g. preemption)
            elif "destroy" not in self.processes and proc_name not in ["create", "destroy"]:
                needs_reset = True

        elif curr_status == Processor.OFF:
            # Don't do anythying if destroy failed but instance doesn't actually exist anymore
            if proc_name == "destroy":
                logging.debug("(%s) Processor already destroyed!" % self.name)
                return

            # Handle cases where we have no idea why the instance doesn't currently exist (e.g. preemption, manual deletion)
            # Retry if 'create' command failed and instance doesn't exist
            if "destroy" not in self.processes and proc_name == "create" and proc_obj.get_num_retries() > 0:
                can_retry = True

            # Reset instance and re-run command if command failed and no sure why instance doesn't exist (e.g. preemption, gets manually deleted)
            elif "destroy" not in self.processes:
                needs_reset = True

        logging.debug("(%s) Curr_status, can_retry, needs_reset are: %s, %s, %s" % (self.name, curr_status, can_retry, needs_reset))

        # Reset instance if its been destroyed/disappeared unexpectedly (i.e. preemption)
        if needs_reset and self.is_preemptible:
            logging.warning("(%s) Instance preempted! Resetting..." % self.name)
            self.reset()

        # Retry start/destroy command
        elif can_retry and proc_name in ["create", "destroy"]:
            time.sleep(3)
            logging.warning("(%s) Process '%s' failed but we still got %s retries left. Re-running command!" % (self.name, proc_name, proc_obj.get_num_retries()))
            self.processes[proc_name] = Process(proc_obj.get_command(),
                                                cmd=proc_obj.get_command(),
                                                stdout=sp.PIPE,
                                                stderr=sp.PIPE,
                                                shell=True,
                                                num_retries=proc_obj.get_num_retries() - 1)

        # Check if the problem is that we cannot SSH in the instance
        elif not self.check_ssh():
            logging.warning("(%s) SSH connection cannot be established! Resetting..." % self.name)
            self.reset()

        # Retry 'run' command
        elif can_retry:
            time.sleep(3)
            logging.warning("(%s) Process '%s' failed but we still got %s retries left. Re-running command!" % (
            self.name, proc_name, proc_obj.get_num_retries()))
            self.run(job_name=proc_name,
                     cmd=proc_obj.get_command(),
                     num_retries=proc_obj.get_num_retries() - 1,
                     docker_image=proc_obj.get_docker_image(),
                     quiet_failure=proc_obj.is_quiet())

        # Raise error if command failed, has no retries, and wasn't caused by preemption
        else:
            self.raise_error(proc_name, proc_obj)

    def __remove_wrk_out_dir(self):

        logging.debug("(%s) CLEARING OUTPUT for checkpoint cleanup, clearing %s." % (self.name, self.wrk_out_dir))

        # Generate the removal command. HAS to be 'sudo' to be able to remove files created by any user.
        cmd = "sudo rm -rf %s*" % self.wrk_out_dir

        # Clean the working output directory
        self.run("cleanup_work_output", cmd)
        self.wait_process("cleanup_work_output")

    def __get_gcloud_start_cmd(self):
        # Create base command
        args = list()
        args.append("gcloud compute instances start %s" % self.name)

        # Specify the zone where instance will exist
        args.append("--zone")
        args.append(self.zone)

        return " ".join(args)

    def __get_gcloud_stop_cmd(self):
        # Create base command
        args = list()
        args.append("gcloud compute instances stop %s" % self.name)

        # Specify the zone where instance will exist
        args.append("--zone")
        args.append(self.zone)

        return " ".join(args)