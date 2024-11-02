import os

class MockTk:
    def __init__(self):
        pass

    def withdraw(self):
        pass

    def Tk(self):
        return self

class MockFileDialog:
    @staticmethod
    def askdirectory(*args, **kwargs):
        mock_directory = "mock_directory"
        if not os.path.exists(mock_directory):
            os.makedirs(mock_directory)
        return mock_directory

    @staticmethod
    def askopenfilename(*args, **kwargs):
        return "mock_file.png"

class MockSimpleDialog:
    @staticmethod
    def askstring(*args, **kwargs):
        return "mock_output_filename"

class MockMessageBox:
    @staticmethod
    def askyesno(title, message):
        return True

tk = MockTk()
filedialog = MockFileDialog()
simpledialog = MockSimpleDialog()
messagebox = MockMessageBox()
