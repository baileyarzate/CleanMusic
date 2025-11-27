
import torchaudio
import inspect

print(inspect.signature(torchaudio.load))
print(torchaudio.load.__doc__)
