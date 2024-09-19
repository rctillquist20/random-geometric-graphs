

def is_float(value):
  try:
    float_value = float(value)
    return float_value != int(float_value)
  except ValueError:
    return False

print(is_float(1.1))
