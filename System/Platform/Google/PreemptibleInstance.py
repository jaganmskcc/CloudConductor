import logging
import subprocess as sp
import time

from System.Platform import Process
from System.Platform import Processor
from Instance import Instance

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
        self.cost_history = []
    
    def reset(self):
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
                            "Resetting as standard insance." % (self.name, self.max_resets))
            # Switch to non-preemptible instance
            self.is_preemptible = False

        # Create cost history record
        prev_price = self.price
        prev_start = self.start_time

        if self.is_preemptible: # still want to use a preemptible image, so, we don't have to recreate
            # Set status to indicate that instance cannot run commands and is destroying
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

            # Wait for startup script to completely finish
            logging.debug("(%s) Waiting for instance to finish starting up..." % self.name)
            self.startup_script_complete = False
            self.wait_until_ready()
            logging.debug("(%s) Instance restarted, continue running processes..." % self.name)
        else:
            logging.debug("(%s) Destroying old instance to create new standard instance..." % self.name)
            # Destroying the instance
            self.destroy()

        # Add record to cost history of last run
        logging.debug("({0}) Appending to cost history: {1}, {2}, {3}".format(self.name, prev_price, prev_start, self.stop_time))
        self.cost_history.append((prev_price, prev_start, self.stop_time))

        # Removing old process(es) that shouldn't be rerun after a restart
        self.processes.pop("create", None)
        self.processes.pop("destroy", None)
        self.processes.pop("start", None)

        # Remove commands that get run during configure_instance()
        for proc in ["configCRCMOD", "install_packages", "configureSSH", "restartSSH"]:
            if proc in self.processes:
                self.processes.pop(proc)

        # Identifying which process(es) need to be recalled
        commands_to_run = list()
        checkpoint_queue = list()
        add_to_checkpoint_queue = False
        fail_to_checkpoint = False
        checkpoint_commands = [i[0] for i in self.checkpoints] # create array of just the commands
        logging.debug("CHECKPOINT COMMANDS: %s" % str(checkpoint_commands))
        cleanup_output = False
        while len(self.processes):
            process_tuple = self.processes.popitem(last=False)
            if add_to_checkpoint_queue: # adding to the checkpoint queue since we're past a checkpoint marker
                checkpoint_queue.append((process_tuple[0], process_tuple[1]))
                if process_tuple[1].has_failed() or not process_tuple[1].complete:
                    # if a process hasn't been completed, a process may have failed before the checkpoint so we need to add all those to the list to be run
                    fail_to_checkpoint = True                
            elif not process_tuple[1].complete or process_tuple[1].has_failed(): # only want to rerun processes that haven't been completed
                commands_to_run.append((process_tuple[0], process_tuple[1]))
            if process_tuple[0] in checkpoint_commands: # hit a checkpoint marker, start adding to the checkpoint_queue after this process
                if fail_to_checkpoint:
                    if cleanup_output:
                        logging.debug("CLEARING OUTPUT for checkpoint cleanup, clearing %s" % (self.wrk_out_dir) )
                        cmd = "rm -rf %s*" % self.wrk_out_dir
                        self.run("cleanup_work_output", cmd)
                        self.wait_process("cleanup_work_output") # wait for the cleanup
                    commands_to_run.extend(checkpoint_queue) # add all the commands in the checkpoint queue to commands to run
                cleanup_output = [d[1] for d in self.checkpoints if d[0] == process_tuple[0]][0]
                logging.debug("CLEAR OUTPUT IS: %s FOR process %s" % (str(cleanup_output), str(process_tuple[0])))
                checkpoint_queue = list() # clear the list if we run into a new checkpoint command
                add_to_checkpoint_queue = True
        if len(checkpoint_queue) > 0: # still have processes in the checkpoint queue
            if fail_to_checkpoint:
                if cleanup_output:
                    logging.debug("CLEARING OUTPUT for checkpoint cleanup, clearing %s" % (self.wrk_out_dir) )
                    cmd = "rm -rf %s*" % self.wrk_out_dir
                    self.run("cleanup_work_output", cmd)
                    self.wait_process("cleanup_work_output") # wait for the cleanup
                commands_to_run.extend(checkpoint_queue) # add all the commands in the checkpoint queue to commands to run
        logging.debug("Commands to be rerun: (%s) " % str([i[0] for i in commands_to_run])) # log names of commands
        
        if not self.is_preemptible: # Recreating the instance as standard instance
            self.create()

        # Rerunning all the commands
        if len(commands_to_run):
            while len(commands_to_run) != 0:
                proc_name, proc_obj = commands_to_run.pop(0)
                self.run(job_name=proc_name,
                         cmd=proc_obj.get_command(),
                         num_retries=proc_obj.get_num_retries(),
                         docker_image=proc_obj.get_docker_image(),
                         quiet_failure=proc_obj.is_quiet())
                self.wait_process(proc_name)

    def get_runtime(self):
        # Compute total runtime across all resets
        # Return 0 if instance hasn't started yet
        if self.start_time is None:
            return 0

        # Instance is still running so register runtime since last start/restart
        elif self.stop_time is None or self.stop_time < self.start_time:
            runtime = time.time() - self.start_time

        # Instance has been stopped
        else:
            runtime = self.stop_time - self.start_time

        # Add previous runtimes from restart history
        for record in self.cost_history:
            end = record[2] if record[2] is not None else 0
            start = record[1] if record[1] is not None else 0
            runtime += end - start
        return runtime

    def compute_cost(self):
        # Compute total cost across all resets
        cost = 0
        if self.start_time is None:
            return 0

        elif self.stop_time is None or self.stop_time < self.start_time:
            cost = (time.time() - self.start_time) * self.price

        else:
            cost = (self.stop_time - self.start_time) * self.price

        for record in self.cost_history:
            end = record[2] if record[2] is not None else 0
            start = record[1] if record[1] is not None else 0
            price = record[0] if record[0] is not None else 0
            cost += (end-start) * price

        return cost/3600

    def handle_failure(self, proc_name, proc_obj):

        # Determine if command can be retried
        can_retry   = False
        needs_reset = False

        logging.warning("(%s) Handling failure for proc '%s'" % (self.name, proc_name))
        logging.debug("(%s) Error code: %s" % (self.name, proc_obj.returncode))
        
        if proc_obj.returncode == 255:
            logging.warning("(%s) Waiting for 60 seconds to make sure instance wasn't preempted..." % self.name)
            time.sleep(60)

        # Raise error if processor is locked
        if self.is_locked() and proc_name != "destroy":
            self.raise_error(proc_name, proc_obj)

        # Check to see if issue was caused by rate limit. If so, cool out for a random time limit
        if "Rate Limit Exceeded" in proc_obj.err:
            self.throttle_api_rate(proc_name, proc_obj)

        # Check again to make sure processor wasn't locked during sleep time
        if self.is_locked() and proc_name != "destroy":
            self.raise_error(proc_name, proc_obj)

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
                return

            # Handle cases where we have no idea why the instance doesn't currently exist (e.g. preemption, manual deletion)
            # Retry if 'create' command failed and instance doesn't exist
            if "destroy" not in self.processes and proc_name == "create" and proc_obj.get_num_retries() > 0:
                can_retry = True

            # Reset instance and re-run command if command failed and no sure why instance doesn't exist (e.g. preemption, gets manually deleted)
            elif "destroy" not in self.processes:
                needs_reset = True


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

    def wait_until_ready(self):
        # Wait until startup-script has completed on instance
        # This signifies that the instance has initialized ssh and the instance environment is finalized
        cycle_count = 1
        # Waiting for 10 minutes for instance metadata to be set to READY
        while cycle_count < 10 and not self.startup_script_complete and not self.is_locked():
            time.sleep(60)
            cycle_count += 1
            self.startup_script_complete = self.poll_startup_script()

        # Throw error if instance locking caused loop to exit
        if self.is_locked():
            logging.debug("(%s) Instance locked while waiting for creation!" % self.name)
            raise RuntimeError("(%s) Instance locked while waiting for creation!" % self.name)

        # Reset if instance not initialized within the alloted timeframe
        elif not self.startup_script_complete:

            # Try creating again if there are still resets
            if self.creation_resets < self.default_num_cmd_retries:
                logging.debug("(%s) Create took more than 10 minutes! Resetting instance!" % self.name)
                self.creation_resets += 1
                self.reset()

            # Throw error if instance still isn't ready after multiple tries
            else:
                logging.debug("(%s) Instance successfully created but "
                              "never became available after %s resets!" %
                              (self.name, self.default_num_cmd_retries))

                raise RuntimeError("(%s) Instance successfully created but never"
                                   " became available after %s resets!" %
                                   self.name, self.default_num_cmd_retries)

    def __get_gcloud_start_cmd(self):
        # Create base command
        args = list()
        args.append("gcloud compute instances start %s" % self.name)

        # Specify the zone where instance will exist
        args.append("--zone")
        args.append(self.zone)

        return " ".join(args)
