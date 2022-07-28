# test_goaltree.py
# Copyright (c) 2022 Dr. Rupert Rebentisch
# Licensed under the MIT license


from .context import tools4zettelkasten as zt
from click.testing import CliRunner


def test_tree_command_in_help_message():
    runner = CliRunner()
    result = runner.invoke(zt.cli.messages, [])
    assert result.exit_code == 0
    assert 'tree' in result.output
    return runner


def test_start_goal_tree_command():
    runner = CliRunner()
    result = runner.invoke(zt.cli.messages, ['tree'])
    # Banner is shown
    assert 'Rupert Rebentisch' in result.output


def test_tree_directory_set_to_invalid_default(tmp_path):
    # default directory does not exist
    runner = CliRunner()
    result = runner.invoke(zt.cli.messages, ['tree'])
    assert 'TREE not set in environment' in result.output
    assert 'will default to' in result.output
    assert ('is not a directory, please set'
            in result.output)
    assert result.exit_code == 1


def test_tree_directory_set_to_valid_default(tmp_path):
    import os
    # default directory exists
    runner_new = CliRunner()
    with runner_new.isolated_filesystem():
        os.mkdir('tree')
        result = runner_new.invoke(zt.cli.messages, ['tree'])
    assert 'TREE not set in environment' in result.output
    assert 'will default to' in result.output
    assert result.exit_code == 0


def test_goal_tree(tmp_path):
    # Oliver is a logical thinking process consultant
    # After a long webex he reviews the mural board and stitches the different
    # cards together to form a goal tree

    # He uses the tools4zettelkasten
    # First he runs the program without any subcommand.
    # He will receive a help message. With all available subcommands.
    # He is looking for the subcommand tree.
    test_tree_command_in_help_message()

    # He starts the tree command.
    # And he will receive a message that the
    # tree directory is set to the default
    test_start_goal_tree_command()

    # Oliver configures the goal creation tool with
    # an evironment variable to specify the path to the tree directory.

    # When he omits the environment variable a default value
    # is created if this directory does not exist yet he gets an error message.
    test_tree_directory_set_to_invalid_default(tmp_path)

    # He can create the directory manually and the the program will work.
    test_tree_directory_set_to_valid_default(tmp_path)

    # Oliver makes a mistake with environment variable.
    # Strating the tool will show an error message.
    # That the directory does not exist.

    # Oliver corrects the environment variable.
    # And the tool shows no error message.

    # Oliver has not created a input subdirectory
    # as subdirectory of the tree directory.
    # The tool will show him a waring message.
    # That the directory does not exist.
    # He will get a message which instructs which directory to create.

    # He strats with the central goal of the goal tree
    # He creates a central goal md file for the goal tree
    # He names the file goal.md and saves it in the stage directory.
    # He invokes the stage command to rename the file to
    # 0_0_Central_Goal_Id.md where id is a unique id.

    # If the goal.md has no header a warning is issued.

    # Oliver starts the tree command. But as there is no file in the
    # tree directory, there is no tree. He will get an error message.
    # Also there is a message that informs him that files in the input
    # directory might have to be moved to the tree parent directory, as
    # the input directory is just for stageing the files.

    # He then moves the file to the tree directory.

    # Oliver will get an error message, because 0_0_... is a second level
    # node and there is no parent node. There will be a message for him,
    # which instructs him to construct the filenames accordingly.

    # Oliver renames the file 0_0_Central_Goal_Id.md to 1_Central_Goal_Id.md.
    # He use the tree command and a graph with just the main goal is created.

    # Oliver prepares two files with key success factors. After stageing,
    # moving them to tree directory he ends up with the following files:
    # 1_Central_Goal_Id.md
    # 1_1_KSF_A.md
    # 1_2_KSF_B.md
    # Oliver uses the tree command to see the two KSF pointing to the Goal.

    assert False
