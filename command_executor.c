#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "command_executor.h"

int check_root_privileges(void) {
    if (geteuid() != 0) {
        fprintf(stderr, "%sError: RED-AI must be run as root (UID 0) only.%s\n",
                COLOR_RED, COLOR_RESET);
        fprintf(stderr, "This tool cannot be executed with sudo or by non-root users.\n");
        fprintf(stderr, "Please log in as root and run directly.\n");
        return -1;
    }
    return 0;
}

int execute_command(const char *command, char *output, int output_size) {
    FILE *fp;
    char buffer[MAX_BUFFER_SIZE];
    int ret = 0;

    output[0] = '\0';

    fp = popen(command, "r");
    if (fp == NULL) {
        snprintf(output, output_size, "Failed to execute command");
        return -1;
    }

    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        strncat(output, buffer, output_size - strlen(output) - 1);
    }

    ret = pclose(fp);

    if (ret != 0) {
        return -1;
    }

    return 0;
}

int execute_command_definition(const CommandDefinition *cmd_def,
                                int dry_run, int interactive) {
    char output[MAX_OUTPUT_SIZE];
    char all_output[MAX_OUTPUT_SIZE * 2];
    int success_count = 0;
    int failed_count = 0;

    all_output[0] = '\0';

    printf("\n%s=== Executing: %s ===%s\n",
           COLOR_CYAN, cmd_def->description, COLOR_RESET);
    printf("%sCategory:%s %s\n", COLOR_BLUE, COLOR_RESET, cmd_def->category);
    printf("%sAction:%s %s\n", COLOR_BLUE, COLOR_RESET, cmd_def->action);
    printf("%sRisk Level:%s %s\n", COLOR_BLUE, COLOR_RESET, cmd_def->risk_level);

    if (cmd_def->requires_reboot) {
        printf("%sWarning: This configuration requires a system reboot.%s\n",
               COLOR_YELLOW, COLOR_RESET);
    }

    if (strcmp(cmd_def->risk_level, "high") == 0) {
        printf("%sWarning: This is a HIGH RISK operation!%s\n",
               COLOR_RED, COLOR_RESET);
    }

    if (dry_run) {
        printf("\n%s[DRY RUN MODE - Commands will not be executed]%s\n",
               COLOR_YELLOW, COLOR_RESET);
    }

    if (interactive && !dry_run) {
        printf("\n%sDo you want to proceed? (yes/no): %s", COLOR_YELLOW, COLOR_RESET);
        char response[10];
        if (fgets(response, sizeof(response), stdin) == NULL ||
            (strcmp(response, "yes\n") != 0 && strcmp(response, "y\n") != 0)) {
            printf("%sOperation cancelled by user.%s\n", COLOR_RED, COLOR_RESET);
            return -2;
        }
    }

    printf("\n%sCommands to execute:%s\n", COLOR_BLUE, COLOR_RESET);

    for (int i = 0; i < cmd_def->command_count; i++) {
        printf("  %d. %s\n", i + 1, cmd_def->commands[i]);

        if (!dry_run) {
            output[0] = '\0';
            printf("     %sExecuting...%s ", COLOR_YELLOW, COLOR_RESET);
            fflush(stdout);

            int ret = execute_command(cmd_def->commands[i], output, sizeof(output));

            if (ret == 0) {
                printf("%s[OK]%s\n", COLOR_GREEN, COLOR_RESET);
                success_count++;
            } else {
                printf("%s[FAILED]%s\n", COLOR_RED, COLOR_RESET);
                failed_count++;
            }

            if (strlen(output) > 0) {
                printf("     Output: %s\n", output);
            }

            strncat(all_output, output, sizeof(all_output) - strlen(all_output) - 1);
            strncat(all_output, "\n", sizeof(all_output) - strlen(all_output) - 1);
        }
    }

    if (!dry_run) {
        printf("\n%s=== Execution Summary ===%s\n", COLOR_CYAN, COLOR_RESET);
        printf("Total commands: %d\n", cmd_def->command_count);
        printf("%sSuccessful: %d%s\n", COLOR_GREEN, success_count, COLOR_RESET);

        if (failed_count > 0) {
            printf("%sFailed: %d%s\n", COLOR_RED, failed_count, COLOR_RESET);
        }

        if (cmd_def->requires_reboot) {
            printf("\n%sREMINDER: Please reboot the system for changes to take effect.%s\n",
                   COLOR_YELLOW, COLOR_RESET);
        }

        return (failed_count == 0) ? 0 : -1;
    } else {
        printf("\n%s[DRY RUN COMPLETE - No commands were executed]%s\n",
               COLOR_YELLOW, COLOR_RESET);
        return 0;
    }
}
