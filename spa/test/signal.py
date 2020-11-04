from django.dispatch import Signal, receiver

# Create a custom signal
ping_signal = Signal(providing_args=["context"])


class SignalDemo(object):
    # function to send the signal
    def ping(self):
        print('PING')
        ping_signal.send(sender=self.__class__, PING=True)


# Function to receive the signal
@receiver(ping_signal)
def pong(**kwargs):
    if kwargs['PING']:
        print('PONG')


demo = SignalDemo()
demo.ping()
