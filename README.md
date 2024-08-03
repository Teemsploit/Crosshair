# Crosshair Application

This is a Python application that displays a crosshair on your screen. It allows you to cycle the crosshair color, toggle its visibility, open/close a console, and more. The application is designed for Windows, administrator privileges recommended.

## Features

- **Crosshair Display**: Draws a crosshair in the center of the screen.
- **Color Cycling**: Change the crosshair color between Red, Green, and Blue.
- **Visibility Toggle**: Show or hide the crosshair.
- **Console Management**: Open and close a console window for debugging or configuration.
- **Key Bindings**: Customize behavior using specific key presses.

## Requirements

- Python 3.x
- `psutil` library (install via `pip install psutil`)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Teemsploit/Crosshair
    ```

2. Navigate into the project directory:

    ```bash
    cd Crosshair
    ```

3. Install the required Python packages:

    ```bash
    pip install psutil
    ```

4. Run the application:

    ```bash
    python crosshair.py
    ```

## Key Bindings

- **Insert**: Cycle through crosshair colors (Red, Green, Blue).
- **Delete**: Toggle the visibility of the crosshair.
- **End**: Open or close the console window.
- **Home**: Show a message with key bindings.
- **Right Arrow**: Close the crosshair.

## Configuration

The application reads and writes its configuration from `crosshair_config.json` located in the `APPDATA` directory. Configuration options include the crosshair color and visibility status.

## Logging

Logs are written to `crosshair.log` in the `APPDATA` directory. This file includes error messages and other runtime information.

## Troubleshooting

- Ensure you are running the application with administrator privileges.
- If you encounter any issues, check the log file for detailed error messages.


## Contact

For any questions or issues, please open an issue on the [GitHub repository](https://github.com/Teemsploit/Crosshair/issues).

---


