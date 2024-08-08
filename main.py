from dnd_GUID import MyWizard
import wx

def main():
    app = wx.App()
    app.MainLoop()
    wizard = MyWizard()
    wizard.RunWizard(wizard.l_page)

if __name__ == '__main__':
    main()