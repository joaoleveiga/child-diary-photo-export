"""GUI wrapper for ChildDiary photo export script.

Provides a simple Tkinter interface for non-technical users to run the export
without using the command line.
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Check if we're running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as bundle, use the temp folder for output
    APP_PATH = sys._MEIPASS
    DEFAULT_OUTPUT = os.path.join(os.path.expanduser('~'), 'ChildDiaryExport')
else:
    # Running in development
    APP_PATH = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_OUTPUT = os.path.join(APP_PATH, 'media')


class ChildDiaryExportGUI:
    """Main GUI application for ChildDiary photo export."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI.

        Parameters
        ----------
        root : tk.Tk
            The root Tkinter window.
        """
        self.root = root
        self.root.title("ChildDiary Photo Export")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Configure styles
        self.configure_styles()

        # Create main container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create form fields
        self.create_form()

        # Create action buttons
        self.create_buttons()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        # Output text area for logs
        self.output_text = tk.Text(
            self.main_frame, height=8, wrap=tk.WORD, state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for output
        scrollbar = ttk.Scrollbar(self.output_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output_text.yview)

        # Running state
        self.running = False

    def configure_styles(self) -> None:
        """Configure custom ttk styles."""
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 11))
        style.configure('TButton', font=('Helvetica', 11))
        style.configure('TEntry', font=('Helvetica', 11))
        style.configure('TCombobox', font=('Helvetica', 11))

    def create_form(self) -> None:
        """Create the form input fields."""
        # Output Directory
        ttk.Label(self.main_frame, text="Output Directory:").pack(
            anchor=tk.W, pady=(0, 2)
        )
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT)
        entry_frame = ttk.Frame(self.main_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 10))

        self.output_dir_entry = ttk.Entry(
            entry_frame, textvariable=self.output_dir_var, width=40
        )
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_button = ttk.Button(
            entry_frame,
            text="Browse...",
            command=self.browse_output_dir,
            width=10,
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Compression
        ttk.Label(self.main_frame, text="Compression:").pack(
            anchor=tk.W, pady=(0, 2)
        )
        self.compress_var = tk.StringVar(value="zip")
        self.compress_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.compress_var,
            values=["zip", "gzip", "bz2", ""],
            state="readonly",
            width=15,
        )
        self.compress_combo.pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(
            self.main_frame,
            text="(Leave empty to disable compression)",
            foreground="gray",
        ).pack(anchor=tk.W, pady=(0, 10))

        # Start Page
        ttk.Label(self.main_frame, text="Start Page:").pack(
            anchor=tk.W, pady=(0, 2)
        )
        self.start_page_var = tk.IntVar(value=1)
        self.start_page_spin = ttk.Spinbox(
            self.main_frame,
            from_=1,
            to=999,
            textvariable=self.start_page_var,
            width=10,
        )
        self.start_page_spin.pack(anchor=tk.W, pady=(0, 10))

    def create_buttons(self) -> None:
        """Create action buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.run_button = ttk.Button(
            button_frame,
            text="Start Export",
            command=self.start_export,
            style='Accent.TButton',
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_export,
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT)

    def browse_output_dir(self) -> None:
        """Open file dialog to select output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get(),
        )
        if directory:
            self.output_dir_var.set(directory)

    def append_output(self, text: str) -> None:
        """Append text to the output area.

        Parameters
        ----------
        text : str
            Text to append.
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_export(self) -> None:
        """Start the export process in a background thread."""
        if self.running:
            return

        # Validate inputs
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Build command line arguments
        args = ['python', 'script.py']

        compress = self.compress_var.get()
        if compress:
            args.extend(['-c', compress])

        args.extend(['-o', output_dir])

        start_page = self.start_page_var.get()
        if start_page > 1:
            args.extend(['-p', str(start_page)])

        # Update UI
        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running...")
        self.append_output(f"Starting export to: {output_dir}")
        if compress:
            self.append_output(f"Compression: {compress}")
        self.append_output(f"Start page: {start_page}")
        self.append_output("-" * 40)

        # Run in background thread
        self.export_thread = threading.Thread(
            target=self.run_export, args=(args,), daemon=True
        )
        self.export_thread.start()

    def run_export(self, args: list[str]) -> None:
        """Run the export command and capture output.

        Parameters
        ----------
        args : list[str]
            Command line arguments.
        """
        try:
            # Use subprocess to run the script
            # In a PyInstaller bundle, we need to use sys.executable
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller bundle
                python_executable = sys.executable
                script_path = os.path.join(
                    os.path.dirname(sys.executable), 'script.py'
                )
                # Reconstruct args with the bundled Python
                bundle_args = [python_executable, script_path]
                for arg in args[1:]:
                    if arg not in ('python', 'script.py'):
                        bundle_args.append(arg)
                cmd = bundle_args
            else:
                cmd = args

            self.append_output(f"Running: {' '.join(cmd)}")
            self.append_output("")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Read output line by line
            for line in process.stdout:
                if line.strip():
                    self.append_output(line.strip())

            return_code = process.wait()

            if return_code == 0:
                self.append_output("")
                self.append_output("✓ Export completed successfully!")
                self.status_var.set("Completed")
                messagebox.showinfo(
                    "Success", "Export completed successfully!"
                )
            else:
                self.append_output("")
                self.append_output(f"✗ Export failed with code: {return_code}")
                self.status_var.set("Failed")

        except Exception as e:
            self.append_output(f"Error: {e}")
            self.append_output("")
            self.append_output("✗ Export failed with exception")
            self.status_var.set("Error")

        finally:
            self.running = False
            self.root.after(0, self.reset_ui)

    def reset_ui(self) -> None:
        """Reset UI after export completes."""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Ready")

    def stop_export(self) -> None:
        """Stop the export process."""
        self.append_output("Stop requested...")
        self.status_var.set("Stopping...")
        # Note: Proper process termination would require tracking the process
        # This is a simple implementation


def main() -> None:
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = ChildDiaryExportGUI(root)

    # Center window on screen
    root.eval('tk::PlaceWindow . center')

    # Set minimum size
    root.minsize(450, 350)

    # Run application
    root.mainloop()


if __name__ == "__main__":
    main()
