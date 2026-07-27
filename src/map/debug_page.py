from PySide6.QtWebEngineCore import QWebEnginePage


class DebugPage(QWebEnginePage):

    def javaScriptConsoleMessage(
        self,
        level,
        message,
        lineNumber,
        sourceID,
    ):
        print(
            f"[JS] {message} ({sourceID}:{lineNumber})"
        )