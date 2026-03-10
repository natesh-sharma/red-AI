#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <getopt.h>
#include "config.h"
#include "command_executor.h"

Config global_config = {0};

static CommandDefinition local_commands[] = {
    {
        .id = "1",
        .category = "kernel",
        .action = "disable",
        .description = "Disable transparent hugepages",
        .commands = {
            "echo never > /sys/kernel/mm/transparent_hugepage/enabled",
            "echo never > /sys/kernel/mm/transparent_hugepage/defrag",
            "grubby --update-kernel=ALL --args=\"transparent_hugepage=never\""
        },
        .command_count = 3,
        .requires_reboot = 1,
        .risk_level = "medium"
    },
    {
        .id = "2",
        .category = "kernel",
        .action = "enable",
        .description = "Enable transparent hugepages",
        .commands = {
            "echo always > /sys/kernel/mm/transparent_hugepage/enabled",
            "echo always > /sys/kernel/mm/transparent_hugepage/defrag",
            "grubby --update-kernel=ALL --args=\"transparent_hugepage=always\""
        },
        .command_count = 3,
        .requires_reboot = 1,
        .risk_level = "medium"
    },
    {
        .id = "3",
        .category = "kdump",
        .action = "configure",
        .description = "Configure kdump crash recovery",
        .commands = {
            "yum install -y kexec-tools",
            "systemctl enable kdump",
            "systemctl start kdump"
        },
        .command_count = 3,
        .requires_reboot = 0,
        .risk_level = "medium"
    },
    {
        .id = "4",
        .category = "kdump",
        .action = "disable",
        .description = "Disable kdump crash recovery",
        .commands = {
            "systemctl stop kdump",
            "systemctl disable kdump"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "low"
    },
    {
        .id = "5",
        .category = "kdump",
        .action = "check",
        .description = "Check kdump status",
        .commands = {
            "systemctl status kdump",
            "kdumpctl showmem"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "low"
    },
    {
        .id = "6",
        .category = "selinux",
        .action = "disable",
        .description = "Disable SELinux",
        .commands = {
            "setenforce 0",
            "sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config"
        },
        .command_count = 2,
        .requires_reboot = 1,
        .risk_level = "high"
    },
    {
        .id = "7",
        .category = "selinux",
        .action = "enable",
        .description = "Enable SELinux in enforcing mode",
        .commands = {
            "setenforce 1",
            "sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config"
        },
        .command_count = 2,
        .requires_reboot = 1,
        .risk_level = "medium"
    },
    {
        .id = "8",
        .category = "selinux",
        .action = "check",
        .description = "Check SELinux status",
        .commands = {
            "getenforce",
            "sestatus"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "low"
    },
    {
        .id = "9",
        .category = "firewall",
        .action = "disable",
        .description = "Disable firewall",
        .commands = {
            "systemctl stop firewalld",
            "systemctl disable firewalld"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "high"
    },
    {
        .id = "10",
        .category = "firewall",
        .action = "enable",
        .description = "Enable firewall",
        .commands = {
            "systemctl enable firewalld",
            "systemctl start firewalld"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "medium"
    },
    {
        .id = "11",
        .category = "firewall",
        .action = "check",
        .description = "Check firewall status",
        .commands = {
            "systemctl status firewalld",
            "firewall-cmd --list-all"
        },
        .command_count = 2,
        .requires_reboot = 0,
        .risk_level = "low"
    },
    {
        .id = "12",
        .category = "system",
        .action = "check",
        .description = "Check system status",
        .commands = {
            "uname -a",
            "uptime",
            "free -h",
            "df -h"
        },
        .command_count = 4,
        .requires_reboot = 0,
        .risk_level = "low"
    }
};

static const int local_command_count = sizeof(local_commands) / sizeof(local_commands[0]);

static void str_to_lower(char *dst, const char *src, size_t size) {
    size_t i;
    for (i = 0; i < size - 1 && src[i]; i++)
        dst[i] = tolower((unsigned char)src[i]);
    dst[i] = '\0';
}

static CommandDefinition *match_command(const char *prompt) {
    char lower_prompt[512];
    str_to_lower(lower_prompt, prompt, sizeof(lower_prompt));

    int best_index = -1;
    int best_score = 0;

    for (int i = 0; i < local_command_count; i++) {
        char lower_desc[512];
        str_to_lower(lower_desc, local_commands[i].description, sizeof(lower_desc));

        int score = 0;
        char desc_copy[512];
        strncpy(desc_copy, lower_desc, sizeof(desc_copy) - 1);
        desc_copy[sizeof(desc_copy) - 1] = '\0';

        char *token = strtok(desc_copy, " ");
        while (token) {
            if (strstr(lower_prompt, token))
                score++;
            token = strtok(NULL, " ");
        }

        /* Also check category and action */
        char lower_cat[128], lower_act[32];
        str_to_lower(lower_cat, local_commands[i].category, sizeof(lower_cat));
        str_to_lower(lower_act, local_commands[i].action, sizeof(lower_act));

        if (strstr(lower_prompt, lower_cat))
            score += 2;
        if (strstr(lower_prompt, lower_act))
            score += 2;

        if (score > best_score) {
            best_score = score;
            best_index = i;
        }
    }

    if (best_index >= 0 && best_score >= 2)
        return &local_commands[best_index];

    return NULL;
}

void print_banner(void) {
    printf("%s", COLOR_CYAN);
    printf("╔════════════════════════════════════════════════════════════╗\n");
    printf("║                                                            ║\n");
    printf("║              RED-AI Configuration Assistant v%s           ║\n", VERSION);
    printf("║                                                            ║\n");
    printf("║   Intelligent system configuration tool for RHEL Linux    ║\n");
    printf("║                  Developed by: Natesh Sharma             ║\n");
    printf("║                                                            ║\n");
    printf("╚════════════════════════════════════════════════════════════╝\n");
    printf("%s\n", COLOR_RESET);
}

void load_config(void) {
    char *url = getenv("SUPABASE_URL");
    char *key = getenv("SUPABASE_SERVICE_ROLE_KEY");

    if (!url || !key) {
        fprintf(stderr, "%sWarning: Supabase environment variables not set.%s\n",
                COLOR_YELLOW, COLOR_RESET);
        fprintf(stderr, "Tool will use local command definitions.\n");
    }

    if (url)
        strncpy(global_config.supabase_url, url, sizeof(global_config.supabase_url) - 1);
    if (key)
        strncpy(global_config.supabase_key, key, sizeof(global_config.supabase_key) - 1);
}

void print_usage(const char *prog_name) {
    printf("Usage: %s [OPTIONS] <prompt>\n\n", prog_name);
    printf("Options:\n");
    printf("  -h, --help              Show this help message\n");
    printf("  -l, --list              List all available configurations\n");
    printf("  -d, --dry-run           Show what would be executed\n");
    printf("  -y, --yes               Skip confirmation prompts\n");
    printf("  -v, --version           Show version information\n\n");
    printf("Examples:\n");
    printf("  %s \"disable transparent hugepages\"\n", prog_name);
    printf("  %s --list\n", prog_name);
    printf("  %s --dry-run \"configure kdump\"\n\n", prog_name);
}

int main(int argc, char *argv[]) {
    int opt;
    int dry_run = 0;
    int skip_confirm = 0;

    struct option long_options[] = {
        {"help", no_argument, 0, 'h'},
        {"dry-run", no_argument, 0, 'd'},
        {"yes", no_argument, 0, 'y'},
        {"version", no_argument, 0, 'v'},
        {0, 0, 0, 0}
    };

    while ((opt = getopt_long(argc, argv, "hdyv", long_options, NULL)) != -1) {
        switch (opt) {
            case 'h':
                print_banner();
                print_usage(argv[0]);
                return 0;
            case 'd':
                dry_run = 1;
                break;
            case 'y':
                skip_confirm = 1;
                break;
            case 'v':
                print_banner();
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    print_banner();
    load_config();

    if (!dry_run && check_root_privileges() != 0) {
        return 1;
    }

    if (optind >= argc) {
        fprintf(stderr, "%sError: No prompt provided.%s\n\n", COLOR_RED, COLOR_RESET);
        print_usage(argv[0]);
        return 1;
    }

    /* Build the full prompt string from remaining args */
    char prompt[512] = {0};
    for (int i = optind; i < argc; i++) {
        if (i > optind)
            strncat(prompt, " ", sizeof(prompt) - strlen(prompt) - 1);
        strncat(prompt, argv[i], sizeof(prompt) - strlen(prompt) - 1);
    }

    printf("%sSearching for matching configuration...%s\n", COLOR_BLUE, COLOR_RESET);
    printf("Prompt: \"%s\"\n", prompt);

    CommandDefinition *matched = match_command(prompt);

    if (matched) {
        int interactive = !skip_confirm;
        return execute_command_definition(matched, dry_run, interactive);
    }

    printf("\n%sNo matching configuration found for: \"%s\"%s\n",
           COLOR_YELLOW, prompt, COLOR_RESET);
    printf("%sTo add custom configurations, insert them into your Supabase%s\n",
           COLOR_BLUE, COLOR_RESET);
    printf("%sdatabase using the command_definitions table.%s\n\n",
           COLOR_BLUE, COLOR_RESET);

    return 1;
}
