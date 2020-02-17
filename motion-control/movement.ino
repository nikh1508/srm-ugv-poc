void manuver(byte v, float current, float desired) {
  Serial.println( "V::"+ String(v)+ "\tCurrent::"+String(current)+"\tDesired::"+String(desired));
  desired = angleDiff(desired, current);
  desired = getYaw() + desired;
  if (desired > 360.0)
    desired -= 360.0;
  else if (desired < 0.0)
    desired += 360.0;
  if (v == 0) {
    bot.rotate(desired);
    }
  else if (v == 1) {
    bot.setHeading(desired);
    bot.move(50, 0);
  }
  else {
    bot.stop();
  }
}
