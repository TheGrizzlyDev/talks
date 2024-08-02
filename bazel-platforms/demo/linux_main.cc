#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>

int main() {
    int fd;
    ssize_t bytes_written;
    const char *data = "Hello, World!\n ";
    
    // Open (or create) a file for writing
    fd = open("hello_world.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1) {
        std::cerr << "Could not open or create file." << std::endl;
        return 1;
    }

    // Write data to the file
    bytes_written = write(fd, data, strlen(data));
    if (bytes_written == -1) {
        std::cerr << "Failed to write to file." << std::endl;
        close(fd);
        return 1;
    }

    std::cout << "Hello, World! written to hello_world.txt" << std::endl;

    // Close the file descriptor
    close(fd);

    return 0;
}
