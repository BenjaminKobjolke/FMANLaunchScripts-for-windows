#
# Load the libraries that are used in these commands.
#
import subprocess
from core.quicksearch_matchers import contains_chars
from fman import DirectoryPaneCommand, show_prompt, show_quicksearch, QuicksearchItem, show_status_message, clear_status_message, save_json, load_json, show_alert
import os
import json
import re
from fman.url import as_human_readable
from fman.url import as_url
from subprocess import run, PIPE

#
# Function:       _GetScriptVars
#
# Description:    This function gets the variables for this
#                 plugin.
#
def _GetScriptVars():
    #
    # Get the scripts directory.
    #
    scriptVars = load_json("LaunchScriptWindows.json")
    if scriptVars is None:
        scriptVars = dict()
        scriptVars['show_output'] = True
        scriptVars['directory'] = os.path.expanduser('~/bin')
        scriptVars['local_shell'] = os.path.expanduser('~/.bashrc')
        scriptVars['command_line_history'] = ['ls -la']
        save_json("LaunchScriptWindows.json", scriptVars)
    return(scriptVars)

#
# Function:    _SaveScriptVars
#
# Description: This function saves a new set of variables
#              for this plugin.
#
def _SaveScriptVars(scriptVars):
    save_json("LaunchScriptWindows.json", scriptVars)

#
# Function:    GoToScriptsDir
#
# Description: This class performs the operation of going
#              to the scripts directory.
#
class GoToScriptsDir(DirectoryPaneCommand):
    #
    # This directory command is for showing the scripts
    # directory in the current Directory Pane.
    #
    def __call__(self):
        scriptDir = _GetScriptVars()
        self.pane.set_path(as_url(os.path.expanduser(scriptDir['directory'] + os.sep)))

#
# Function:   SetShellScript
#
# Description: This function sets the path to the users
#              shell script or initializing the shell.
#
class SetShellScript(DirectoryPaneCommand):
    def __call__(self):
        scriptVars = _GetScriptVars()
        shellFile, status = show_prompt("What is your shell script?")
        shellFile = os.path.expanduser(shellFile)
        if not os.path.isfile(shellFile):
            show_alert("Not a real file.")
        else:
            scriptVars['local_shell'] = shellFile
            _SaveScriptVars(scriptVars)

#
# Function:   SetShowOutput
#
# Description: This function sets the flag to show
#              the output of the script.
#
class SetShowOutput(DirectoryPaneCommand):
    def __call__(self):
        scriptVars = _GetScriptVars()
        scriptVars['show_output'] = True
        _SaveScriptVars(scriptVars)

#
# Function:   SetNotShowOutput
#
# Description: This function sets the flag to not show
#              the output of the script.
#
class SetNotShowOutput(DirectoryPaneCommand):
    def __call__(self):
        scriptVars = _GetScriptVars()
        scriptVars['show_output'] = False
        _SaveScriptVars(scriptVars)

#
# Function:   SetTheScriptsDirectory(DirectoryPaneCommand)
#
# Description: This class performs the function of
#              setting the Scripts Directory location.
#
class SetTheScriptsDirectory(DirectoryPaneCommand):
    #
    # This directory command is for setting the
    # Scripts Directory location.
    #
    def __call__(self):
        show_status_message('Setting the Scripts Directory')
        selected_files = self.pane.get_selected_files()
        if len(selected_files) >= 1 or (len(selected_files) == 0 and self.get_chosen_files()):
            if len(selected_files) == 0 and self.get_chosen_files():
                selected_files.append(self.get_chosen_files()[0])
            dirName = as_human_readable(selected_files[0])
            if os.path.isfile(dirName):
                #
                # It's a file, not a directory. Get the directory
                # name for this file's parent directory.
                #
                dirName = os.path.dirname(dirName)
            scriptDir = _GetScriptVars()
            scriptDir['directory'] = dirName
            _SaveScriptVars(scriptDir)
        else:
            show_alert("Directory not selected.")
        clear_status_message()

#
# Function:    LaunchScript
#
# Description: This class performs the function of
#              launching a script from the scripts
#              directory.
#
class LaunchScript(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Launching a Script...')
        result = show_quicksearch(self._suggest_script)
        if result:
            #
            # Launch the script given. Show the output.
            #
            query, script = result

            #
            # Get the variables for this plugin
            #
            scriptVars = _GetScriptVars()

            #
            # Run the script.
            #  

           
            comm = [scriptVars['directory'] + "/" + script]
            #files = self.get_chosen_files()
            files = self.pane.get_selected_files()
            
            if len(files) >= 1:
                for file in files:                    
                    comm.append(as_human_readable(file))
            else:
                currentDir = as_human_readable(self.pane.get_path())
                comm.append(currentDir)            
            
            #show_alert(comm)
            Output = run(comm,shell=False)
            
        clear_status_message()

    def _suggest_script(self, query):
        scripts = ["No scripts are setup."]
        #
        # Get a list of scripts.
        #
        scriptDir = _GetScriptVars()
        scripts = os.listdir(scriptDir['directory'])

        #
        # Suggested one to the user and let them pick.
        #
        for script in scripts:
            scriptName = script.strip()
            if scriptName != "":
                match = False
                if query:
                    match = contains_chars(script.lower(), query.lower())
                else:
                    match = True
                if scriptName[0] == '.' or scriptName[0] == 'L' or scriptName[0] == 'R':
                    match = False
                if match:
                    yield QuicksearchItem(scriptName)

#
# Function:    EditScript
#
# Description: This class performs the function of
#              editing a script from the scripts
#              directory.
#
class EditScript(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Editing a Script...')
        result = show_quicksearch(self._suggest_script)
        if result:
            #
            # Launch the script given. Show the output.
            #
            query, script = result

            #
            # Get the variables for this plugin
            #
            scriptVars = _GetScriptVars()

            #
            # Edit the script file.
            #
            if self.pane.is_command_visible('open_with_editor'):
                self.pane.run_command('open_with_editor',{'url': as_url(scriptVars['directory'] + os.sep + script)})
            else:
                show_alert("OpenWithEditor command not found.")
        clear_status_message()

    def _suggest_script(self, query):
        scripts = ["No scripts are setup."]
        #
        # Get a list of scripts.
        #
        scriptDir = _GetScriptVars()
        scripts = os.listdir(scriptDir['directory'])

        #
        # Suggested one to the user and let them pick.
        #
        for script in scripts:
            scriptName = script.strip()
            if scriptName != "":
                match = False
                if query:
                    match = contains_chars(script.lower(), query.lower())
                else:
                    match = True
                if scriptName[0] == '.' or scriptName[0] == 'L' or scriptName[0] == 'R':
                    match = False
                if match:
                    yield QuicksearchItem(scriptName)

#
# Function:    CreateScript
#
# Description: This class performs the function of
#              creating a script and then editing the newly
#              created script from the scripts
#              directory.
#
class CreateScript(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Creating a Script...')
        scriptVars = _GetScriptVars()
        script, flags = show_prompt("New Script Name?")
        newScript = scriptVars['directory'] + os.sep + script
        if os.path.isdir(newScript):
            show_alert("This is a directory.")
        else:
            if os.path.isfile(newScript):
                show_alert("Script already exists.")
            else:
                #
                # Create the script file.
                #
                fp = open(newScript,"w+")
                fp.write("@echo off\n")
                fp.write("setlocal enabledelayedexpansion\n\n")
                fp.write("set argCount=0\n")
                fp.write("for %%x in (%*) do (\n")
                fp.write("\tset /A argCount+=1\n")
                fp.write("\tset \"argVec[!argCount!]=%%~x\"\n")
                fp.write(")\n\n")
                fp.write("echo Number of arguments to process: %argCount%\n\n")
                fp.write("for /L %%i in (1,1,%argCount%) do (\n")
                fp.write("\tREM !argVec[%%i] will either contain all the files or it will be just the directory,\n")
                fp.write("\tREM if no files were selected\n")
                fp.write("\techo %%i- \"!argVec[%%i]!\"\n")
                fp.write(")\n\n")
                fp.write("pause")
                fp.close()
                os.chmod(newScript,0o755)

                #
                # Edit the script file.
                #
                if self.pane.is_command_visible('open_with_editor'):
                    self.pane.run_command('open_with_editor',{'url': as_url(newScript)})
        clear_status_message()

#
# Function:    LaunchNPMScript
#
# Description: This class performs the function of
#              launching an npm script.
#
class LaunchNpmScript(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Launching a Script...')
        if os.path.isfile(as_human_readable(self.pane.get_path()) + os.path.sep + 'package.json'):
            npmPackagePath = as_human_readable(self.pane.get_path()) + os.path.sep + 'package.json'
            npmPackagePtr = open(npmPackagePath,"r")
            npmPackage = json.loads(npmPackagePtr.read())
            npmPackagePtr.close()
            if 'scripts' in npmPackage:
                result = show_quicksearch(self._suggest_script)
                if result:
                    #
                    # Launch the script given. Show the output.
                    #
                    query, script = result

                    #
                    # Get the variables for this plugin
                    #
                    scriptVars = _GetScriptVars()

                    #
                    # Run the script.
                    #
                    saveDir = os.getcwd()
                    os.chdir(as_human_readable(self.pane.get_path()) + os.path.sep)
                    Output = run("source " + scriptVars['local_shell'] + "; npm run " + script,stdout=PIPE,shell=True)
                    os.chdir(saveDir)
                    if Output.returncode == 0:
                        if scriptVars['show_output']:
                            show_alert(Output.stdout.decode("utf-8"))
                    else:
                        show_alert("Command line error.")
            else:
                show_alert("No scripts defined.")
        else:
            show_alert("Not a NPM project directory.")
        clear_status_message()

    def _suggest_script(self, query):
        scripts = []
        npmPackagePath = as_human_readable(self.pane.get_path()) + os.path.sep + 'package.json'
        npmPackagePtr = open(npmPackagePath,"r")
        npmPackage = json.loads(npmPackagePtr.read())
        npmPackagePtr.close()
        for scriptName, command in npmPackage["scripts"].items():
            scripts.append(scriptName)

        #
        # Suggested one to the user and let them pick.
        #
        for script in scripts:
            if script.strip() != "":
                scriptName = script
                match = contains_chars(scriptName.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(scriptName, highlight=match)

class LaunchMaskScript(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Launching a Mask Script...')
        if os.path.isfile(as_human_readable(self.pane.get_path()) + os.path.sep + 'package.json'):
            npmPackagePath = as_human_readable(self.pane.get_path()) + os.path.sep + 'maskfile.md'
            npmPackagePtr = open(npmPackagePath,"r")
            npmPackage = json.loads(npmPackagePtr.read())
            npmPackagePtr.close()
            result = show_quicksearch(self._suggest_script)
            if result:
                #
                # Launch the script given. Show the output.
                #
                query, script = result

                #
                # Get the variables for this plugin
                #
                scriptVars = _GetScriptVars()

                #
                # Run the script.
                #
                saveDir = os.getcwd()
                os.chdir(as_human_readable(self.pane.get_path()) + os.path.sep)
                Output = run("source " + scriptVars['local_shell'] + "; mask " + script,stdout=PIPE,shell=True)
                os.chdir(saveDir)
                if Output.returncode == 0:
                    if scriptVars['show_output']:
                        show_alert(Output.stdout.decode("utf-8"))
                else:
                    show_alert("Command line error.")
        else:
            show_alert("Not a Mask project directory.")
        clear_status_message()

    def _suggest_script(self, query):
        scripts = []
        maskPackagePath = as_human_readable(self.pane.get_path()) + os.path.sep + 'maskfile.md'
        maskPackagePtr = open(npmPackagePath,"r")
        maskScript = npmPackagePtr.read()
        maskPackagePtr.close()
        for scriptName, command in scriptNames:
            scripts.append(scriptName)

        #
        # Suggested one to the user and let them pick.
        #
        for script in scripts:
            if script.strip() != "":
                scriptName = script
                match = contains_chars(scriptName.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(scriptName, highlight=match)

#
# Function:    RunCommandLine
#
# Description: This class performs the function of
#              getting a command line from the user
#              and running it. It allows for the selection
#              from past command lines.
#
class RunCommandLine(DirectoryPaneCommand):
    #
    # This directory command is for launching
    # a selected script.
    #
    def __call__(self):
        show_status_message('Launching a Command Line...')
        result = show_quicksearch(self._suggest_script)
        if result:
            #
            # Launch the script given. Show the output.
            #
            query, script = result
            if query != '':
                script = query

            #
            # Get the variables for this plugin
            #
            scriptVars = _GetScriptVars()

            #
            # Save the command line.
            #
            scriptVars['command_line_history'].append(script)

            #
            # Set the environment variables for the scripts to use.
            #
            os.putenv('cd', as_human_readable(self.pane.get_path()))
            panes = self.pane.window.get_panes()
            os.putenv('lp', as_human_readable(panes[0].get_path()))
            os.putenv('lpf',as_human_readable(panes[0].get_file_under_cursor()))
            os.putenv('rp', as_human_readable(panes[1].get_path()))
            os.putenv('rpf',as_human_readable(panes[1].get_file_under_cursor()))
            os.putenv('cf', os.path.basename(as_human_readable(self.pane.get_file_under_cursor())))

            #
            # Run the script.
            #
            saveDir = os.getcwd()
            os.chdir(as_human_readable(self.pane.get_path()) + os.path.sep)
            scriptLine = "source " + scriptVars['local_shell'] + "; " + script
            Output = run(scriptLine,stdout=PIPE,shell=True)
            os.chdir(saveDir)
            if Output.returncode == 0:
                if scriptVars['show_output']:
                    show_alert(Output.stdout.decode("utf-8"))
                scriptVars['command_line_history'] = CleanCommandLineHistory(scriptVars['command_line_history'])
                _SaveScriptVars(scriptVars)
            else:
                show_alert("Command line error.")
        clear_status_message()

    def _suggest_script(self, query):
        scriptVars = _GetScriptVars()
        scripts = scriptVars['command_line_history']

        #
        # Suggested one to the user and let them pick.
        #
        for script in scripts:
            if script.strip() != "":
                scriptName = script
                match = contains_chars(scriptName.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(scriptName, highlight=match)


def CleanCommandLineHistory(history_list):
    newList = []
    commandLine = ""
    for cmd in sorted(history_list):
        if commandLine == cmd:
            commandLine = cmd
        else:
            commandLine = cmd
            newList.append(cmd)
    return(newList)
