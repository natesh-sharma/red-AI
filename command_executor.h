#ifndef COMMAND_EXECUTOR_H
#define COMMAND_EXECUTOR_H

#include "config.h"

int execute_command(const char *command, char *output, int output_size);
int execute_command_definition(const CommandDefinition *cmd_def,
                                int dry_run, int interactive);
int check_root_privileges(void);

#endif
