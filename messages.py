class color:
    black       = '\033[30m'
    red         = '\033[31m'
    green       = '\033[32m'
    orange      = '\033[33m'
    blue        = '\033[34m'
    purple      = '\033[35m'
    cyan        = '\033[36m'
    white       = '\033[37m'
    lightred    = '\033[91m'
    lightgreen  = '\033[92m'
    yellow      = '\033[93m'
    lightblue   = '\033[94m'
    pink        = '\033[95m'
    lightcyan   = '\033[96m'
    
    reset       = '\033[0m'   
    bold        = '\033[1m'
    underline   = '\033[4m'

class message: 
    
    @classmethod
    def error(cls, msg):
        print(color.lightred + msg + color.reset)

    @classmethod
    def warning(cls, msg):
        print(color.yellow + msg + color.reset)

    @classmethod
    def success(cls, msg):
        print(color.green + msg + color.reset)

    @classmethod
    def custom(cls, s, clr=color.white):
        print(clr + s + color.reset)

    @classmethod
    def separator(cls, n=20, sep='-', clr=color.white):
        print(clr + n*sep + color.reset)
    
    @classmethod
    def inseparator(cls, s, n=20, sep='-', clr=color.white):
        print(clr + n*sep)
        print(s)
        print(n*sep + color.reset)


if __name__ == '__main__':
    message.error('error message')
    message.warning('warning message')
    message.success('success message')
    message.separator()
    message.custom('custom message')
    message.custom('custom message', color.red)
    message.custom('custom message', color.green)
    message.custom('custom message', color.orange)
    message.custom('custom message', color.blue)
    message.custom('custom message', color.purple)
    message.custom('custom message', color.cyan)
    message.custom('custom message', color.white)
    message.custom('custom message', color.lightred)
    message.custom('custom message', color.lightgreen)
    message.custom('custom message', color.yellow)
    message.custom('custom message', color.lightblue)
    message.custom('custom message', color.pink)
    message.custom('custom message', color.lightcyan)
