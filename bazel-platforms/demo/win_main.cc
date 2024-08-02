#include <windows.h>
#include <iostream>

int main() {
    HANDLE hFile;
    DWORD dwBytesWritten = 0;
    LPCSTR data = "Hello, World!\r\n";
    
    // Create a new file or open an existing one
    hFile = CreateFile(
        "hello_world.txt",         // File name
        GENERIC_WRITE,             // Open for writing
        0,                         // Do not share
        NULL,                      // Default security
        CREATE_ALWAYS,             // Overwrite existing file
        FILE_ATTRIBUTE_NORMAL,     // Normal file
        NULL                       // No template
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        std::cerr << "Could not open or create file." << std::endl;
        return 1;
    }

    // Write data to the file
    BOOL bErrorFlag = WriteFile(
        hFile,                   // Open file handle
        data,                    // Start of data to write
        strlen(data),            // Number of bytes to write
        &dwBytesWritten,         // Number of bytes that were written
        NULL                     // No overlapped structure
    );

    if (!bErrorFlag) {
        std::cerr << "Failed to write to file." << std::endl;
        CloseHandle(hFile);
        return 1;
    }

    std::cout << "Hello, World! written to hello_world.txt" << std::endl;

    // Close the file handle
    CloseHandle(hFile);

    return 0;
}
