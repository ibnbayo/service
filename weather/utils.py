from datetime import datetime

def validate_date(date_text):

  try:
    if 'T' in date_text:
      datetime.fromisoformat(date_text)
    else:
      datetime.date.fromisoformat(date_text)

  except ValueError:
    return False
  
  return True