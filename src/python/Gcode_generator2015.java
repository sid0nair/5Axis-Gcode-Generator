import java.util.*;
import java.io.*;
import static java.lang.Math.*;

/*
Generator for 5-axis g-code.
All the methods are returning a LinkedList which are containing GcodeNode with all the information of a point in the g-code path.
All the methods expect that the base of the part are centered in origin of the printer.
*/
public class Gcode_generator {
    public double plasticPerkvadMM = 0.2078760;

    /**
     * Sphere along X- and Y-axis
     * @param resolution The distance between each generated point in the g-code
     * @param layerDistance The distance between each plastic thread
     * @param layerHeight The height of the printed layer
     * @param circleRadius Radius of the sphere printed on
     * @param platformHeight The height up to the beginning of the 5-axis print
     * @param layers Amount of layers printed with the 5-axis system
     * @param cOffset Offset on C-axis to avoid same changing point in g-code
     * @return LinkedList containing the g-code nodes
     */
    public LinkedList<GcodeNode> sphereXY(double resolution, double layerDistance, double layerHeight, double circleRadius, double platformHeight, int layers, double cOffset) {
        LinkedList<GcodeNode> tmpList = new LinkedList<GcodeNode>();
        
        // Angles for A-axis and C-axis
        double a, c = 0.0;
        double layer = 1, sphereRadius;
        double aResolution;
        boolean dirUp = false;
        double[] sphericalCap;
        
        a = dirUp ? 90.0 : 0.0;
        while (layer <= layers) {
            sphereRadius = (circleRadius + (layerHeight * layer));
            // Using arc length to find the resolution along the A-axis
            aResolution = (180 * layerDistance) / (PI * sphereRadius);
            if (a == 0.0) a += aResolution;
            while (dirUp ? a >= 0 : a <= 90) {
                sphericalCap = findSphericalCap(a, sphereRadius);
                tmpList.addAll(gcodeXYCircle(resolution, layerHeight, sphericalCap[1], sphericalCap[0], c, platformHeight));
                c += cOffset;
                if (c > 360) c = c - 360;
                a = dirUp ? a - aResolution : a + aResolution;
            }
            a = dirUp ? a + aResolution : a - aResolution;
            layer++;
            dirUp = !dirUp;
        }
        return tmpList;
    }

    /**
     * Sphere along X- and Z-axis
     * @param resolution The distance between each generated point in the g-code
     * @param layerDistance The distance between each plastic thread
     * @param layerHeight The height of the printed layer
     * @param circleRadius Radius of the sphere printed on
     * @param platformHeight The height up to the beginning of the 5-axis print
     * @param layers Amount of layers printed with the 5-axis system
     * @return LinkedList containing the g-code nodes
     */
    public LinkedList<GcodeNode> sphereXZ(double resolution, double layerDistance, double layerHeight, double circleRadius, double platformHeight, int layers) {
        LinkedList<GcodeNode> tmpList = new LinkedList<GcodeNode>();
        double cResolution, sphereRadius;
        double[] sphericalCap;
        int layer = 1, circleCounter = 1;
        boolean xDirection = true, yDirection = true;
        
        while (layer <= layers) {
            sphereRadius = circleRadius + layerHeight * layer;
            // Using arc length to find the resolution along the C-axis
            cResolution = (180 * layerDistance) / (PI * sphereRadius);
            while (yDirection ? cResolution * circleCounter < 180 : cResolution * circleCounter > 0) {
                sphericalCap = findSphericalCap(cResolution * circleCounter, sphereRadius);
                tmpList.addAll(gcodeXZCircle(resolution, sphericalCap[1], sphericalCap[0], platformHeight, layerHeight, xDirection));
                xDirection = !xDirection;
                circleCounter = yDirection ? circleCounter + 1 : circleCounter - 1;
            }
            layer++;
            yDirection = !yDirection;
        }
        return tmpList;
    }

    /**
     * Circles along X- and Y-axis
     * @param resolution The distance between each generated point in the g-code
     * @param layerDistance The distance between each plastic thread
     * @param layerHeight The height of the printed layer
     * @param circleRadius Radius of the cylinder printed on
     * @param platformHeight The height to the top of the beginning of the 5-axis print
     * @param layersHeight Amount of layers in height
     * @param layersWidth Amount of layers in width
     * @param cOffset Offset on C-axis to avoid same changing point in g-code
     * @return LinkedList containing the g-code nodes
     */
    public LinkedList<GcodeNode> circleXY(double resolution, double layerDistance, double layerHeight, double circleRadius, double platformHeight, int layersHeight, int layersWidth, double cOffset) {
        LinkedList<GcodeNode> tmpList = new LinkedList<GcodeNode>();
        double z, r;
        int layerHeightCounter = 1;
        int layerBreadthCounter = 0;
        double c = 0.0;
        boolean direction = true;
        
        z = platformHeight;
        while (layerHeightCounter <= layersHeight) {
            r = circleRadius + layerHeight * layerHeightCounter;
            layerBreadthCounter = direction ? 0 : layersWidth - 1;
            while (direction ? layerBreadthCounter < layersWidth : layerBreadthCounter >= 0) {
                z = platformHeight - layerDistance * layerBreadthCounter;
                tmpList.addAll(gcodeXYCircle(resolution, layerHeight, r, 0.0, c, z));
                layerBreadthCounter = direction ? layerBreadthCounter + 1 : layerBreadthCounter - 1;
                c += cOffset;
                if (c > 360) c -= 360;
            }
            direction = !direction;
            layerHeightCounter++;
        }
        return tmpList;
    }

    /**
     * Method to find length from center and radius of a Spherical cap
     * @param circleAngle Angle to point in sphere
     * @param r Radius of sphere
     * @return array containing
     * 0: z Distance from center
     * 1: a_r Radius of new circle
     */
    private double[] findSphericalCap(double circleAngle, double r) {
        double[] tmp = new double[2];
        double h;
        tmp[0] = r * sin(toRadians(90 - circleAngle));
        h = r - tmp[0];
        tmp[1] = sqrt(h * (2 * r - h));
        return tmp;
    }

    /**
     * Method to create g-code for circles along the X- and Y-axis.
     * @param resolution The distance between each generated point in the g-code
     * @param layerHeight The layer height of the print
     * @param radius Radius of the circle
     * @param z Height of the circle in the sphere
     * @param zOffset Height of the platform the circle are printed on
     * @param cStart Offset along the C-axis to avoid same changing point in the g-code
     * @return LinkedList containing the g-code nodes
     */
    private LinkedList<GcodeNode> gcodeXYCircle(double resolution, double layerHeight, double radius, double z, double zOffset, double cStart) {
        LinkedList<GcodeNode> tmpList = new LinkedList<GcodeNode>();
        GcodeNode tmpGN;
        double x, y, c = cStart;
        Double e = null;
        double[] tmp;
        double cRes = (180 * resolution) / (PI * radius);
        boolean first = true;
        
        while (c <= 360 + cStart) {
            x = radius * sin(toRadians(c));
            y = radius * cos(toRadians(c));
            tmp = cartCorToSphere(x, y, z);
            tmp = cartAngleToVector(tmp[1], tmp[2]);
            // Do not extrude to the first point, since this is a rapid move.
            if (first) first = false;
            else e = resolution * layerHeight * plasticPerkvadMM;
            tmpGN = new GcodeNode(x, y, z + zOffset, tmp[0], tmp[1], tmp[2], e);
            tmpList.add(tmpGN);
            c += cRes;
        }
        return tmpList;
    }

    /**
     * Method to create g-code for half circles along the X- and Z-axis.
     * @param resolution The distance between each generated point in the g-code
     * @param layerHeight The layer height of the print
     * @param radius Radius of the circle
     * @param y Distance between sphere origin and this circle
     * @param zOffset Height of the platform the circle are printed on
     * @param direction Which direction this circle are going
     * @return LinkedList containing the g-code nodes
     */
    private LinkedList<GcodeNode> gcodeXZCircle(double resolution, double layerHeight, double radius, double y, double zOffset, boolean direction) {
        LinkedList<GcodeNode> tmpList = new LinkedList<GcodeNode>();
        GcodeNode tmpGN;
        int counter = 0;
        double circleCounter, aResolution, z, x;
        Double e = null;
        double[] tmp;
        boolean first = true;
        // Using arc length to find the resolution along the A-axis
        aResolution = (180 * resolution) / (PI * radius);
        circleCounter = 180 / aResolution;
        counter = direction ? 0 : (int) circleCounter;
        
        while (direction ? aResolution * counter < 180 : aResolution * counter > 0) {
            z = sin(toRadians(aResolution * counter)) * radius;
            x = cos(toRadians(aResolution * counter)) * radius;
            counter = direction ? counter + 1 : counter - 1;
            tmp = cartCorToSphere(x, y, z);
            tmp = cartAngleToVector(tmp[1], tmp[2]);
            // Do not extrude to the first point, since this is a rapid move.
            if (first) first = false;
            else e = resolution * layerHeight * plasticPerkvadMM;
            tmpGN = new GcodeNode(x, y, z + zOffset, tmp[0], tmp[1], tmp[2], e);
            tmpList.add(tmpGN);
        }
        return tmpList;
    }

    /**
     * Method to find vector values for a point in a sphere based on the spherical angles to that point.
     * @param a A-axis angle
     * @param c C-axis angle
     * @return double[] Vector values:
     * 0: I
     * 1: J
     * 2: K
     */
    private double[] cartAngleToVector(double a, double c) {
        double[] tmp = new double[3];
        tmp[0] = cos(toRadians(c)) * sin(toRadians(a));
        tmp[1] = sin(toRadians(c)) * sin(toRadians(a));
        tmp[2] = cos(toRadians(a));
        return tmp;
    }

    /**
     * Method to find angles and radius to a point in a sphere based on the Cartesian coordinates to that point.
     * @param x Point on X-axis
     * @param y Point on Y-axis
     * @param z Point on Z-axis
     * @return double[] Angles and radius to a point in a sphere:
     * 0: r
     * 1: a
     * 2: c
     */
    private double[] cartCorToSphere(double x, double y, double z) {
        double[] tmp = new double[3];
        tmp[0] = sqrt(x * x + y * y + z * z);
        tmp[1] = toDegrees(acos(z / tmp[0]));
        tmp[2] = toDegrees(atan2(y, x));
        return tmp;
    }

    /*
     * Node class for storing and creating string of generated g-code
     */
    class GcodeNode {
        public Double x, y, z, i, j, k, e, f;
        
        public GcodeNode(Double x, Double y, Double z, Double i, Double j, Double k, Double e) {
            this.x = x;
            this.y = y;
            this.z = z;
            this.i = i;
            this.j = j;
            this.k = k;
            this.e = e;
            this.f = null;
        }

        public String toString() {
            String tmp = "G1";
            if (x != null) tmp += String.format(" X%.3f", x);
            if (y != null) tmp += String.format(" Y%.3f", y);
            if (z != null) tmp += String.format(" Z%.3f", z);
            if (i != null) tmp += String.format(" I%.5f", i);
            if (j != null) tmp += String.format(" J%.5f", j);
            if (k != null) tmp += String.format(" K%.5f", k);
            if (f != null) tmp += String.format(" F%.5f", f);
            if (e != null) tmp += String.format(" E%.5f", e);
            return tmp;
        }
    }

    public static void main(String[] args) {
        Gcode_generator generator = new Gcode_generator();
        double resolution = 0.1;
        double layerDistance = 0.2;
        double layerHeight = 0.2;
        double circleRadius = 10.0;
        double platformHeight = 0.0;
        int layers = 20;
        double cOffset = 1.0;

        LinkedList<GcodeNode> gcodeList = generator.sphereXY(resolution, layerDistance, layerHeight, circleRadius, platformHeight, layers, cOffset);

        try (PrintWriter writer = new PrintWriter(new File("gcode_output2015.gcode"))) {
            for (GcodeNode node : gcodeList) {
                writer.println(node.toString());
            }
            System.out.println("G-code successfully written to gcode_output2015.gcode");
        } catch (FileNotFoundException e) {
            System.err.println("Error writing to file: " + e.getMessage());
        }
    }
}
