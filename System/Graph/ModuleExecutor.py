import logging
import os

from System.Platform import StorageHelper, DockerHelper, Platform

class ModuleExecutor(object):

    def __init__(self, task_id, processor, workspace, docker_image=None):
        self.task_id        = task_id
        self.processor      = processor
        self.workspace      = workspace
        self.storage_helper = StorageHelper(self.processor)
        self.docker_helper  = DockerHelper(self.processor)
        self.docker_image   = docker_image

        # Create workspace directory structure
        self.__create_workspace()

    def load_input(self, inputs):

        # List of jobs that have been started in process of loading input
        job_names = []

        # Pull docker image if necessary
        if self.docker_image is not None:
            docker_image_name = self.docker_image.get_image_name().split("/")[0]
            docker_image_name = docker_image_name.replace(":","_")
            job_name = "docker_pull_%s" % docker_image_name
            self.docker_helper.pull(self.docker_image.get_image_name(), job_name=job_name)
            job_names.append(job_name)

        # Load input files
        # Inputs: list containing remote files, local files, and docker images
        src_seen = []
        dest_seen = []
        count = 1
        batch_size = 5
        loading_counter = 0
        for task_input in inputs:

            # Don't transfer local files
            if ":" not in task_input.get_path():
                continue

            # Directory where input will be transferred
            dest_dir = self.workspace.get_wrk_dir()

            # Input filename after transfer (None = same as src)
            dest_filename = None

            # Case: Transfer file into wrk directory if its not already there
            if task_input.get_transferrable_path() not in src_seen:

                # Get name of file that's going to be transferred
                src_path = task_input.get_transferrable_path()
                job_name = "load_input_%s_%s_%s" % (self.task_id, task_input.get_type(), count)
                logging.debug("Input path: %s, transfer path: %s" % (task_input.get_path(), src_path))

                # Check to see if sample name is provided for the current file and add it if there is
                if task_input.sample_name is not None:
                    dest_filename = "{0}_{1}".format(task_input.sample_name, task_input.filename)
                else:
                    dest_filename = task_input.filename

                # Generate complete transfer path
                dest_path = os.path.join(dest_dir, dest_filename)

                # Check to see if transferring file would overwrite existing file
                if dest_path in dest_seen:
                    # Add unique tag to destination filename to prevent overwrite
                    dest_filename = "{0}_{1}".format(Platform.generate_unique_id(), dest_filename)
                    dest_path = os.path.join(dest_dir, dest_filename)

                # Else set the destination path to the destination dir and keep original filename
                else:
                    dest_filename = None
                    dest_path = dest_dir

                # Show the final log file
                logging.debug("Destination: {0}".format(dest_path))

                # Move file to dest_path
                self.storage_helper.mv(src_path=src_path,
                                       dest_path=dest_path,
                                       job_name=job_name)
                loading_counter += 1
                
                # Add transfer path to list of remote paths that have been transferred to local workspace
                src_seen.append(src_path)
                count += 1
                job_names.append(job_name)
                
                # If loading_counter is batch_size, clear out queue
                if loading_counter >= batch_size:
                    logging.debug("Batch size reached on task {0}".format(
                        self.task_id))
                    # Wait for all processes to finish
                    while len(job_names):
                        self.processor.wait_process(job_names.pop())
                    loading_counter = 0

            # Update path after transferring to wrk directory and add to list of files in working directory
            task_input.update_path(new_dir=dest_dir, new_filename=dest_filename)
            dest_seen.append(task_input.get_path())
            logging.debug("Updated path: %s" % task_input.get_path())

        # Wait for all processes to finish
        for job_name in job_names:
            self.processor.wait_process(job_name)

        # Recursively give every permission to all files we just added
        logging.info("(%s) Final workspace perm. update for task '%s'..." % (self.processor.name, self.task_id))
        self.__grant_workspace_perms(job_name="grant_final_wrkspace_perms")

    def run(self, cmd, job_name=None):

        # Check or create job name
        if job_name is None:
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
        count = 1
        job_names = []

        # List of output file paths. We create this list to ensure the files are not being overwritten
        output_filepaths = []

        for output_file in outputs:
            if output_file.get_type() in final_output_types:
                dest_dir = final_output_dir
            else:
                dest_dir = tmp_output_dir

            # Calculate output file size
            job_name = "get_size_%s_%s_%s" % (self.task_id, output_file.get_type(), count)
            file_size = self.storage_helper.get_file_size(output_file.get_path(), job_name=job_name)
            output_file.set_size(file_size)

            # Check if there already exists a file with the same name on the bucket
            destination_path = "{0}/{1}/".format(dest_dir.rstrip("/"), output_file.get_filename())
            if destination_path in output_filepaths:

                # Change the destination directory for a new subdirectory
                dest_dir = "{0}/{1}/".format(dest_dir.rstrip("/"), len(output_filepaths))

                # Regenerate the destination path
                new_destination_path = "{0}/{1}".format(dest_dir.rstrip("/"), output_file.get_filename())

                # Add the new path to the output file paths
                output_filepaths.append(new_destination_path)

            else:
                # Just add the new path to the list of output file paths
                output_filepaths.append(destination_path)

            # Transfer to correct output directory
            job_name = "save_output_%s_%s_%s" % (self.task_id, output_file.get_type(), count)
            curr_path = output_file.get_transferrable_path()
            self.storage_helper.mv(curr_path, dest_dir, job_name=job_name)

            # Update path of output file to reflect new location
            job_names.append(job_name)
            output_file.update_path(new_dir=dest_dir)
            logging.debug("(%s) Transferring file '%s' from old path '%s' to new path '%s' ('%s')" % (
                self.task_id, output_file.get_type(), curr_path, output_file.get_path(), output_file.get_transferrable_path()))

            count += 1

        # Wait for transfers to complete
        for job_name in job_names:
            self.processor.wait_process(job_name)

        # Wait for output files to finish transferring
        self.processor.wait()

    def save_logs(self):
        # Move log files to final output log directory
        log_files = os.path.join(self.workspace.get_wrk_log_dir(), "*")
        final_log_dir = self.workspace.get_final_log_dir()
        self.storage_helper.mv(log_files, final_log_dir, job_name="return_logs", log=False, wait=True)

    def __create_workspace(self):
        # Create all directories specified in task workspace

        logging.info("(%s) Creating workspace for task '%s'..." % (self.processor.name, self.task_id))
        for dir_type, dir_obj in  self.workspace.get_workspace().items():
            self.storage_helper.mkdir(dir_obj, job_name="mkdir_%s" % dir_type, wait=True)

        # Set processor wrk, log directories
        self.processor.set_wrk_dir(self.workspace.get_wrk_dir())
        self.processor.set_wrk_out_dir(self.workspace.get_wrk_out_dir())
        self.processor.set_log_dir(self.workspace.get_wrk_log_dir())

        # Give everyone all the permissions on working directory
        logging.info("(%s) Updating workspace permissions..." % self.processor.name)
        self.__grant_workspace_perms(job_name="grant_initial_wrkspace_perms")

        # Wait for all the above commands to complete
        logging.info("(%s) Successfully created workspace for task '%s'!" % (self.processor.name, self.task_id))

    def __grant_workspace_perms(self, job_name):
        cmd = "sudo chmod -R 777 %s" % self.workspace.get_wrk_dir()
        self.processor.run(job_name=job_name, cmd=cmd)
        self.processor.wait_process(job_name)
