from tkinter import Tk

from ui import OptionCalculatorUI


def on_closing():
    if app.market_data_tab.canvas:  # Check canvas in the MarketDataTab class
        app.market_data_tab.canvas.get_tk_widget().destroy()  # Destroy the canvas widget if it exists
    root.destroy()  # Proceed to close the app


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
