import os
import pandas as pd

def count_shoot(udp,receive_packet,track_ball_position,track_robot_position):
    packet=receive_packet(udp)
    frame=packet.detection
    