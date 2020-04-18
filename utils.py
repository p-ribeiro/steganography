import progressbar

PROGRESS_BAR = None

def setProgressBar(maxValue):
    global PROGRESS_BAR

    widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Timer(), ' ']

    PROGRESS_BAR = progressbar.ProgressBar(widgets = widgets, max_value = maxValue)



def showProgress(value):
    global PROGRESS_BAR
    PROGRESS_BAR.update(value)