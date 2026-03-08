#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
// POSIX includes
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#endif

#define MAX_ROUTES 100
#define BUFFER_SIZE 1024

// Route definition
typedef void (*handler_func)();
typedef struct {
    char* method;
    char* path;
    handler_func handler;
} Route;

// Global state
static Route routes[MAX_ROUTES];
static int route_count = 0;
static SOCKET server_socket;
static int running = 0;
#ifdef _WIN32
static HANDLE server_thread;
#else
static pthread_t server_thread;
#endif

// Request context for the current thread
#ifdef _WIN32
__declspec(thread) static char* g_request_body = NULL;
__declspec(thread) static char* g_url_params = NULL;
__declspec(thread) static char* g_query_params = NULL;
__declspec(thread) static char* g_request_headers = NULL;
__declspec(thread) static SOCKET g_client_socket;
#else
__thread static char* g_request_body = NULL;
__thread static char* g_url_params = NULL;
__thread static char* g_query_params = NULL;
__thread static char* g_request_headers = NULL;
__thread static int g_client_socket;
#endif

// Forward declarations
void* handle_connection(void* client_socket);

void enhanced_server_start(int port) {
    if (running) {
        printf("Server is already running.\n");
        return;
    }

#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        printf("Failed to initialize Winsock\n");
        return;
    }
#endif

    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        printf("Could not create socket\n");
        return;
    }

    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        printf("Bind failed\n");
        return;
    }

    listen(server_socket, 3);
    running = 1;
    printf("Server started on port %d\n", port);

    // Main accept loop in a separate thread
#ifdef _WIN32
    server_thread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)handle_connection, NULL, 0, NULL);
#else
    pthread_create(&server_thread, NULL, handle_connection, NULL);
#endif
}

void enhanced_server_stop() {
    if (running) {
        running = 0;
        closesocket(server_socket);
#ifdef _WIN32
        WSACleanup();
#endif
        printf("Server stopped.\n");
    }
}

void enhanced_server_route(char* method, char* path, handler_func handler) {
    if (route_count < MAX_ROUTES) {
        routes[route_count].method = strdup(method);
        routes[route_count].path = strdup(path);
        routes[route_count].handler = handler;
        route_count++;
    }
}

void* handle_connection(void* arg) {
    struct sockaddr_in client_addr;
    int client_len = sizeof(struct sockaddr_in);
    SOCKET client_socket;

    while (running && (client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_len))) {
        g_client_socket = client_socket;
        char buffer[BUFFER_SIZE] = {0};
        recv(client_socket, buffer, BUFFER_SIZE - 1, 0);

        char method[16], path[256];
        sscanf(buffer, "%s %s", method, path);

        // Simple routing
        for (int i = 0; i < route_count; i++) {
            if (strcmp(method, routes[i].method) == 0 && strcmp(path, routes[i].path) == 0) {
                routes[i].handler();
                break;
            }
        }

        closesocket(client_socket);
    }
    return NULL;
}

void enhanced_send_response(int status_code, char* body) {
    char response[BUFFER_SIZE];
    sprintf(response, "HTTP/1.1 %d OK\r\nContent-Type: text/plain\r\nContent-Length: %zu\r\n\r\n%s", status_code, strlen(body), body);
    send(g_client_socket, response, strlen(response), 0);
}

// Mock implementations for request context getters
char* enhanced_get_request_body() { return g_request_body ? strdup(g_request_body) : strdup(""); }
char* enhanced_get_url_param(char* name) { return strdup("param_val"); }
char* enhanced_get_query_param(char* name) { return strdup("query_val"); }
char* enhanced_get_request_header(char* name) { return strdup("header_val"); }

char* enhanced_get_env(char* name) {
#ifdef _WIN32
    char* value = NULL;
    size_t len;
    _dupenv_s(&value, &len, name);
    return value ? value : "";
#else
    char* value = getenv(name);
    return value ? value : "";
#endif
}
