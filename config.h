#ifndef CONFIG_H
#define CONFIG_H

#define VERSION "1.0.0"
#define MAX_BUFFER_SIZE 8192
#define MAX_COMMAND_SIZE 2048
#define MAX_OUTPUT_SIZE 16384

#define COLOR_RESET   "\033[0m"
#define COLOR_RED     "\033[1;31m"
#define COLOR_GREEN   "\033[1;32m"
#define COLOR_YELLOW  "\033[1;33m"
#define COLOR_BLUE    "\033[1;34m"
#define COLOR_CYAN    "\033[1;36m"

typedef struct {
    char id[64];
    char category[128];
    char action[32];
    char description[512];
    char commands[10][512];
    int command_count;
    int requires_reboot;
    char risk_level[16];
} CommandDefinition;

typedef struct {
    char supabase_url[256];
    char supabase_key[512];
} Config;

extern Config global_config;

void load_config(void);
void print_banner(void);

#endif
