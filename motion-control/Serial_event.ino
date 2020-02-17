void TIM3_Setup()
{
  cli();
  TCCR3A = 0;
  TCCR3B = 0;
  TCNT3 = 0;
  OCR3A = 750;
  TCCR3B |= (1 << WGM32);
  TCCR3B |= (1 << CS32) | (1 << CS30);
  TIMSK3 |= (1 << OCIE3A);
  sei();
}


void serialFlush()
{
  while (PORT.available() > 0)
    char ch = PORT.read();
}

void decodeData(byte toDecode[], byte totalRecvd, byte &decodedByteCount, byte decodedBytes[])
{
  constexpr byte startMarker = 254;
  constexpr byte endMarker = 255;
  constexpr byte specialByte = 253;
  for (int i = 1; i < (totalRecvd - 1); i++)
  {
    byte x = toDecode[i];
    if (x == specialByte)
      x += toDecode[++i];
    decodedBytes[decodedByteCount++] = x;
  }
}

void serialEvent() {
  static bool firstCall = true;
  static bool inProgress = false;
  static byte bytesRecvd = 0;
  static byte tempBuffer[20];
  constexpr byte toRead = 9;
  static byte decoded_data[10]; // 9-bytes required | 1 + 4 + 4
  if (firstCall)
  {
    firstCall = false;
    serialFlush();
  }
  while (PORT.available())
  {
    byte x = PORT.read();
    //    Serial.println(x);
    if (x == startMarker)
    {
      inProgress = true;
      bytesRecvd = 0;
    }
    if (inProgress)
      tempBuffer[bytesRecvd++] = x;
    if (x == endMarker)
    {
      inProgress = false;
      firstCall = true;
      byte decodedByteCount = 0;
      decodeData(tempBuffer, bytesRecvd, decodedByteCount, decoded_data);
      if (decodedByteCount == toRead)
      {
        // Change Variables Here
        velocity_recv = decoded_data[0];
        memcpy(&angle_current_recv, decoded_data + 1, sizeof(angle_desired_recv));
        memcpy(&angle_desired_recv, decoded_data + 5, sizeof(angle_current_recv));
      }
      else {
        Serial.println("Received Incorrect Bytes");
      }
    }
  }
}
