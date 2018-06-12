import logging
import os

from System.Platform import StorageHelper, DockerHelper, Processor

class ModuleExecutor(object):

    def __init__(self, task_id, processor, workspace, docker_image=None):
        self.task_id        = task_id
        self.processor      = processor
        self.workspace      = workspace
        self.storage_helper = StorageHelper(self.processor)
        self.docker_helper  = DockerHelper(self.processor)
        self.docker_image   = docker_image

    def load_input(self, inputs):

        if self.processor.get_status() is Processor.OFF:
            # Create processor if it's off
            logging.info("Creating processor '%s' for task '%s'!" % (self.processor.get_name(), self.task_id))
            self.processor.create()

        # Create workspace directory structure
        self.__create_workspace()

        # Pull docker image if necessary
        if self.docker_image is not None:
            self.docker_helper.pull(self.docker_image.get_image_name())

        # Load input files
        # Inputs: list containing remote files, local files, and docker images
        seen = []
        for task_input in inputs:

            # Case: Transfer file into wrk directory if its not already there
            if task_input.get_transferrable_path() not in seen:

                # Transfer file to workspace directory
                src_path = task_input.get_transferrable_path()
                logging.debug("Input path: %s, transfer path: %s" %(task_input.get_path(), src_path))
                self.storage_helper.mv(src_path=src_path,
                                       dest_path=self.workspace.get_wrk_dir())

                # Add transfer path to list of remote paths that have been transferred to local workspace
                seen.append(src_path)

            # Update path after transferring to wrk directory
            task_input.update_path(new_dir=self.workspace.get_wrk_dir())
            logging.debug("Updated path: %s" % task_input.get_path())

        # Wait for all processes to finish
        self.processor.wait()

        # Recursively give every permission to all files we just added
        logging.info("(%s) Final workspace perm. update for task '%s'..." % (self.processor.name, self.task_id))
        self.__grant_workspace_perms(job_name="grant_final_wrkspace_perms")
        self.processor.wait_process("grant_final_wrkspace_perms")

    def run(self, cmd):
        # Job name
        job_name = self.task_id
        # Get name of docker image where command should be run (if any)
        docker_image_name = None if self.docker_image is None else self.docker_image.get_image_name()
        # Begin running job and return stdout, stderr after job has finished running
        self.processor.run(job_name, cmd, docker_image=docker_image_name)
        return self.processor.wait_process(job_name)

    def save_output(self, outputs, final_output_types):
        # Return output files to workspace output dir

        # Get workspace places for output files
        final_output_dir = self.workspace.get_output_dir()
        tmp_output_dir = self.workspace.get_tmp_output_dir()

        for output_file in outputs:
            if output_file.get_type() in final_output_types:
                dest_dir = final_output_dir
            else:
                dest_dir = tmp_output_dir

            # Calculate output file size
            file_size = self.storage_helper.get_file_size(output_file.get_path())
            output_file.set_size(file_size)

            # Transfer to correct output directory
            curr_path = output_file.get_transferrable_path()
            self.storage_helper.mv(curr_path, dest_dir)

            # Update path of output file to reflect new location
            output_file.update_path(new_dir=dest_dir)

        # Wait for output files to finish transferring
        self.processor.wait()

    def save_logs(self):
        # Move log files to final output log directory
        log_files = os.path.join(self.workspace.get_wrk_log_dir(), "*")
        final_log_dir = self.workspace.get_final_log_dir()
        self.storage_helper.mv(log_files, final_log_dir)
        self.processor.wait()

    def __create_workspace(self):
        # Create all directories specified in task workspace

        logging.info("(%s) Creating workspace for task '%s'..." % (self.processor.name, self.task_id))
        for dir_type, dir_obj in  self.workspace.get_workspace().iteritems():
            self.storage_helper.mkdir(dir_obj, job_name="mkdir_%s" % dir_type, wait=True)

        # Set processor wrk, log directories
        self.processor.set_wrk_dir(self.workspace.get_wrk_dir())
        self.processor.set_log_dir(self.workspace.get_wrk_log_dir())

        # Give everyone all the permissions on working directory
        logging.info("(%s) Updating workspace permissions..." % self.processor.name)
        self.__grant_workspace_perms(job_name="grant_initial_wrkspace_perms")

        # Wait for all the above commands to complete
        self.processor.wait()
        logging.info("(%s) Successfully created workspace for task '%s'!" % (self.processor.name, self.task_id))

    def __grant_workspace_perms(self, job_name):
        cmd = "sudo chmod -R 777 %s" % self.workspace.get_wrk_dir()
        self.processor.run(job_name=job_name, cmd=cmd)
