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

    if (check_root_privileges() != 0) {
        return 1;
    }

    if (optind >= argc) {
        fprintf(stderr, "%sError: No prompt provided.%s\n\n", COLOR_RED, COLOR_RESET);
        print_usage(argv[0]);
        return 1;
    }

    printf("%sDemo mode - Configuration tool initialized successfully%s\n",
           COLOR_GREEN, COLOR_RESET);
    printf("\nYour prompt: ");
    for (int i = optind; i < argc; i++) {
        printf("%s ", argv[i]);
    }
    printf("\n");

    printf("%sTo add custom configurations, insert them into your Supabase%s\n",
           COLOR_BLUE, COLOR_RESET);
    printf("%sdatabase using the command_definitions table.%s\n\n",
           COLOR_BLUE, COLOR_RESET);

    return 0;
}
