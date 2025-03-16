import ydlidar
import time
import math
import pygame
import sys
import os

# --- Pygame Setup ---
pygame.init()
width, height = 800, 800
center_x, center_y = width // 2, height // 2
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("YDLIDAR Scan Visualization")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
scale = 40 # Pixels per meter (adjust as needed based on range_max)

# --- YDLIDAR Setup ---
print("Initializing YDLIDAR...")
ydlidar.os_init()
ports = ydlidar.lidarPortList()
port = "/dev/ttyUSB0" # Default, might need changing

for key, value in ports.items():
    port = value;
    print(port);

laser = ydlidar.CYdLidar()

# --- Configure YDLIDAR (Adjust based on X3 Pro specs and needs) ---
# Referencing the wrapper constants and typical values
laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200) # Common for X3/X4
laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE) # X3 is Triangle
laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0) # Typical 5-12 Hz range
laser.setlidaropt(ydlidar.LidarPropSampleRate, 7) # 3-9 KHz typical, 5 is a guess
laser.setlidaropt(ydlidar.LidarPropSingleChannel, True)
laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0) # X3 Pro spec is ~12m
laser.setlidaropt(ydlidar.LidarPropMinRange, 0.08) # Typical min range
laser.setlidaropt(ydlidar.LidarPropIntenstiy, False) # X3 Pro doesn't have intensity

# --- Initialize and Turn On ---
print("Initializing connection...")
ret = laser.initialize()
if not ret:
    print(f"Failed to initialize Lidar on port {port}.")
    print(f"Error: {laser.DescribeError()}")
    ydlidar.os_shutdown()
    sys.exit(1)
print("Initialization successful.")

print("Turning on Lidar...")
ret = laser.turnOn()
if not ret:
    print("Failed to turn on Lidar.")
    print(f"Error: {laser.DescribeError()}")
    laser.disconnecting()
    ydlidar.os_shutdown()
    sys.exit(1)
print("Lidar is ON.")

scan = ydlidar.LaserScan()
running = True

# --- Main Loop ---
try:
    while running and ydlidar.os_isOk():
        # --- Pygame Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Get Lidar Scan ---
        r = laser.doProcessSimple(scan)

        if r:
            # --- New Scan Received ---
            # print(f"Scan received [{scan.stamp}]: {scan.points.size()} points, {1.0/scan.config.scan_time:.2f} Hz")

            # --- Drawing ---
            screen.fill(BLACK) # Clear screen
            pygame.draw.circle(screen, RED, (center_x, center_y), 5) # Draw lidar center

            for point in scan.points:
                angle = point.angle # Radians
                range_m = point.range # Meters

                # Filter out invalid points
                if range_m > scan.config.min_range and range_m < scan.config.max_range:
                    # Convert polar to Cartesian
                    x = range_m * math.cos(angle)
                    y = range_m * math.sin(angle)

                    # Convert meters to pixels and adjust for screen coordinates
                    screen_x = center_x + int(x * scale)
                    screen_y = center_y - int(y * scale) # Invert Y

                    # Draw the line from center to point (if within bounds)
                    if 0 <= screen_x < width and 0 <= screen_y < height:
                        # Use a dimmer color for the lines so they don't overwhelm
                        LINE_COLOR = (100, 100, 100)
                        pygame.draw.line(screen, LINE_COLOR, (center_x, center_y), (screen_x, screen_y), 1)
                        # Optional: Draw a small white dot at the end point for clarity
                        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 2)

            pygame.display.flip() # Update the display

        else:
            # print("Waiting for scan...")
            time.sleep(0.01)

        time.sleep(0.01)


except KeyboardInterrupt:
    print("Ctrl+C detected. Shutting down.")
    running = False
finally:
    # --- Cleanup ---
    print("Turning off Lidar...")
    laser.turnOff()
    print("Disconnecting Lidar...")
    laser.disconnecting()
    print("Shutting down Pygame...")
    pygame.quit()
    print("Shutting down YDLIDAR system...")
    ydlidar.os_shutdown()
    print("Done.")
    sys.exit(0)