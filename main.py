from tkinter import Tk

from ui import OptionCalculatorUI


def on_closing():
    # Check if there is a canvas and destroy it before closing the window
    if app.canvas:
        app.canvas.get_tk_widget().destroy()

    # Make sure the window is properly destroyed, and the app exits
    root.quit()  # Stop the Tkinter main loop
    root.destroy()  # Close the main window to ensure Python exits completely


def main():
    global root, app
    root = Tk()
    root.title("OptiCal - Option Calculator")

    # Get the screen width and height, and set the window size to match
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    app = OptionCalculatorUI(root)

    # Bind the window close event to the on_closing function
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()
