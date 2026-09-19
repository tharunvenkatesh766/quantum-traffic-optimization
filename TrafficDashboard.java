import java.awt.*;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import javax.swing.*;
import javax.swing.border.EmptyBorder;

public class TrafficDashboard extends JFrame {

    private static final String API =
            "http://127.0.0.1:8000";

    private final JLabel backendStatus =
            new JLabel("● CONNECTING...");

    private final JTextArea details =
            new JTextArea();

    private final JLabel[] vehicleLabels =
            new JLabel[6];

    private final JLabel[] queueLabels =
            new JLabel[6];

    private final JLabel[] densityLabels =
            new JLabel[6];

    private final JLabel[] signalLabels =
            new JLabel[6];

    public TrafficDashboard() {

        setTitle(
                "Quantum Traffic Optimization Dashboard"
        );

        setSize(1200, 800);

        setDefaultCloseOperation(
                JFrame.EXIT_ON_CLOSE
        );

        setLocationRelativeTo(null);

        JPanel main =
                new JPanel(
                        new BorderLayout(12, 12)
                );

        main.setBorder(
                new EmptyBorder(
                        15,
                        15,
                        15,
                        15
                )
        );

        // =====================================================
        // HEADER
        // =====================================================

        JPanel header =
                new JPanel(
                        new BorderLayout()
                );

        JLabel title =
                new JLabel(
                        "QUANTUM TRAFFIC OPTIMIZATION"
                );

        title.setFont(
                new Font(
                        "Arial",
                        Font.BOLD,
                        26
                )
        );

        backendStatus.setFont(
                new Font(
                        "Arial",
                        Font.BOLD,
                        14
                )
        );

        header.add(
                title,
                BorderLayout.WEST
        );

        header.add(
                backendStatus,
                BorderLayout.EAST
        );

        main.add(
                header,
                BorderLayout.NORTH
        );

        // =====================================================
        // TRAFFIC NETWORK
        // =====================================================

        JPanel network =
                new JPanel(
                        new GridLayout(
                                2,
                                3,
                                12,
                                12
                        )
                );

        network.setBorder(
                BorderFactory.createTitledBorder(
                        "LIVE TRAFFIC NETWORK"
                )
        );

        String[] ids = {
                "J1",
                "J2",
                "J3",
                "J4",
                "J5",
                "J6"
        };

        for (int i = 0; i < 6; i++) {

            network.add(
                    createIntersectionCard(
                            i,
                            ids[i]
                    )
            );
        }

        main.add(
                network,
                BorderLayout.CENTER
        );

        // =====================================================
        // BUTTONS
        // =====================================================

        JPanel buttons =
                new JPanel(
                        new GridLayout(
                                1,
                                6,
                                8,
                                8
                        )
                );

        JButton trafficButton =
                new JButton("TRAFFIC");

        JButton quantumButton =
                new JButton("QUANTUM");

        JButton classicalButton =
                new JButton("CLASSICAL");

        JButton emergencyButton =
                new JButton("EMERGENCY");

        JButton performanceButton =
                new JButton("PERFORMANCE");

        JButton refreshButton =
                new JButton("REFRESH");

        buttons.add(trafficButton);
        buttons.add(quantumButton);
        buttons.add(classicalButton);
        buttons.add(emergencyButton);
        buttons.add(performanceButton);
        buttons.add(refreshButton);

        // =====================================================
        // DETAILS AREA
        // =====================================================

        details.setEditable(false);

        details.setFont(
                new Font(
                        "Monospaced",
                        Font.PLAIN,
                        14
                )
        );

        details.setLineWrap(true);

        details.setWrapStyleWord(true);

        details.setText(
                "Quantum Traffic Optimization Dashboard\n\n"
                        + "Waiting for traffic data..."
        );

        JScrollPane scroll =
                new JScrollPane(details);

        scroll.setPreferredSize(
                new Dimension(
                        1000,
                        190
                )
        );

        JPanel bottom =
                new JPanel(
                        new BorderLayout(
                                10,
                                10
                        )
                );

        bottom.add(
                buttons,
                BorderLayout.NORTH
        );

        bottom.add(
                scroll,
                BorderLayout.CENTER
        );

        main.add(
                bottom,
                BorderLayout.SOUTH
        );

        setContentPane(main);

        // =====================================================
        // BUTTON ACTIONS
        // =====================================================

        trafficButton.addActionListener(
                e -> loadTraffic()
        );

        quantumButton.addActionListener(
                e -> callAPI(
                        "/optimization",
                        "QUANTUM OPTIMIZATION"
                )
        );

        classicalButton.addActionListener(
                e -> callAPI(
                        "/classical",
                        "CLASSICAL OPTIMIZATION"
                )
        );

        emergencyButton.addActionListener(
                e -> callAPI(
                        "/emergency",
                        "EMERGENCY GREEN CORRIDOR"
                )
        );

        performanceButton.addActionListener(
                e -> callAPI(
                        "/performance",
                        "CLASSICAL VS QUANTUM PERFORMANCE"
                )
        );

        refreshButton.addActionListener(
                e -> {
                    checkBackend();
                    loadTraffic();
                }
        );

        // =====================================================
        // INITIAL LOAD
        // =====================================================

        checkBackend();

        loadTraffic();

        // =====================================================
        // AUTOMATIC REFRESH
        // Every 5 seconds
        // =====================================================

        Timer timer =
                new Timer(
                        5000,
                        e -> {
                            checkBackend();
                            loadTraffic();
                        }
                );

        timer.start();
    }

    // =========================================================
    // CREATE INTERSECTION CARD
    // =========================================================

    private JPanel createIntersectionCard(
            int index,
            String id
    ) {

        JPanel card =
                new JPanel(
                        new BorderLayout(
                                5,
                                5
                        )
                );

        card.setBorder(
                BorderFactory.createLineBorder(
                        Color.GRAY,
                        2
                )
        );

        card.setBackground(
                new Color(
                        245,
                        245,
                        245
                )
        );

        JLabel name =
                new JLabel(
                        id,
                        SwingConstants.CENTER
                );

        name.setFont(
                new Font(
                        "Arial",
                        Font.BOLD,
                        24
                )
        );

        JPanel information =
                new JPanel(
                        new GridLayout(
                                3,
                                1
                        )
                );

        information.setOpaque(false);

        vehicleLabels[index] =
                new JLabel(
                        "Vehicles: --",
                        SwingConstants.CENTER
                );

        queueLabels[index] =
                new JLabel(
                        "Queue: --",
                        SwingConstants.CENTER
                );

        densityLabels[index] =
                new JLabel(
                        "Density: --",
                        SwingConstants.CENTER
                );

        information.add(
                vehicleLabels[index]
        );

        information.add(
                queueLabels[index]
        );

        information.add(
                densityLabels[index]
        );

        signalLabels[index] =
                new JLabel(
                        "● UNKNOWN",
                        SwingConstants.CENTER
                );

        signalLabels[index].setFont(
                new Font(
                        "Arial",
                        Font.BOLD,
                        18
                )
        );

        signalLabels[index].setForeground(
                Color.GRAY
        );

        card.add(
                name,
                BorderLayout.NORTH
        );

        card.add(
                information,
                BorderLayout.CENTER
        );

        card.add(
                signalLabels[index],
                BorderLayout.SOUTH
        );

        return card;
    }

    // =========================================================
    // CHECK BACKEND
    // =========================================================

    private void checkBackend() {

        new Thread(
                () -> {

                    try {

                        getAPI("/health");

                        SwingUtilities.invokeLater(
                                () -> {

                                    backendStatus.setText(
                                            "● BACKEND ONLINE"
                                    );

                                    backendStatus.setForeground(
                                            new Color(
                                                    0,
                                                    140,
                                                    0
                                            )
                                    );
                                }
                        );

                    } catch (Exception e) {

                        SwingUtilities.invokeLater(
                                () -> {

                                    backendStatus.setText(
                                            "● BACKEND OFFLINE"
                                    );

                                    backendStatus.setForeground(
                                            Color.RED
                                    );
                                }
                        );
                    }

                }
        ).start();
    }

    // =========================================================
    // LOAD TRAFFIC
    // =========================================================

    private void loadTraffic() {

        new Thread(
                () -> {

                    try {

                        String json =
                                getAPI(
                                        "/traffic"
                                );

                        SwingUtilities.invokeLater(
                                () -> {

                                    details.setText(
                                            "========== LIVE TRAFFIC ==========\n\n"
                                                    + formatJSON(json)
                                    );

                                    updateTrafficCards(
                                            json
                                    );
                                }
                        );

                    } catch (Exception e) {

                        SwingUtilities.invokeLater(
                                () -> {

                                    details.setText(
                                            "ERROR CONNECTING TO PYTHON BACKEND\n\n"
                                                    + e.getMessage()
                                    );
                                }
                        );
                    }

                }
        ).start();
    }

    // =========================================================
    // UPDATE TRAFFIC CARDS
    // =========================================================

    private void updateTrafficCards(
            String json
    ) {

        String[] ids = {
                "J1",
                "J2",
                "J3",
                "J4",
                "J5",
                "J6"
        };

        for (
                int i = 0;
                i < ids.length;
                i++
        ) {

            String id =
                    ids[i];

            int start =
                    json.indexOf(
                            "\"" + id + "\""
                    );

            if (start == -1) {

                start =
                        json.indexOf(id);
            }

            if (start == -1) {
                continue;
            }

            int end =
                    json.indexOf(
                            "}",
                            start
                    );

            if (end == -1) {

                end =
                        json.length();
            }

            String block =
                    json.substring(
                            start,
                            end
                    );

            int vehicles =
                    findNumber(
                            block,
                            "vehicles"
                    );

            if (vehicles == -1) {

                vehicles =
                        findNumber(
                                block,
                                "vehicle_count"
                        );
            }

            int queue =
                    findNumber(
                            block,
                            "queue"
                    );

            if (queue == -1) {

                queue =
                        findNumber(
                                block,
                                "queue_length"
                        );
            }

            int density =
                    findNumber(
                            block,
                            "density"
                    );

            String signal =
                    findText(
                            block,
                            "signal"
                    );

            if (signal == null) {

                signal =
                        findText(
                                block,
                                "status"
                        );
            }

            if (vehicles >= 0) {

                vehicleLabels[i].setText(
                        "Vehicles: " +
                                vehicles
                );
            }

            if (queue >= 0) {

                queueLabels[i].setText(
                        "Queue: " +
                                queue
                );
            }

            if (density >= 0) {

                densityLabels[i].setText(
                        "Density: " +
                                density +
                                "%"
                );
            }

            if (signal != null) {

                updateSignal(
                        signalLabels[i],
                        signal
                );
            }
        }
    }

    // =========================================================
    // FIND NUMBER FROM JSON
    // =========================================================

    private int findNumber(
            String text,
            String key
    ) {

        try {

            String search =
                    "\"" +
                            key +
                            "\"";

            int position =
                    text.indexOf(
                            search
                    );

            if (position == -1) {
                return -1;
            }

            int colon =
                    text.indexOf(
                            ":",
                            position
                    );

            if (colon == -1) {
                return -1;
            }

            String number =
                    text.substring(
                            colon + 1
                    ).trim();

            StringBuilder result =
                    new StringBuilder();

            for (
                    int i = 0;
                    i < number.length();
                    i++
            ) {

                char c =
                        number.charAt(i);

                if (
                        Character.isDigit(c)
                                ||
                        (
                                c == '-'
                                        &&
                                result.length() == 0
                        )
                ) {

                    result.append(c);

                } else if (
                        result.length() > 0
                ) {

                    break;
                }
            }

            if (
                    result.length() > 0
            ) {

                return Integer.parseInt(
                        result.toString()
                );
            }

        } catch (Exception ignored) {
        }

        return -1;
    }

    // =========================================================
    // FIND TEXT FROM JSON
    // =========================================================

    private String findText(
            String text,
            String key
    ) {

        try {

            String search =
                    "\"" +
                            key +
                            "\"";

            int position =
                    text.indexOf(
                            search
                    );

            if (position == -1) {
                return null;
            }

            int colon =
                    text.indexOf(
                            ":",
                            position
                    );

            if (colon == -1) {
                return null;
            }

            int firstQuote =
                    text.indexOf(
                            "\"",
                            colon + 1
                    );

            if (firstQuote == -1) {
                return null;
            }

            int secondQuote =
                    text.indexOf(
                            "\"",
                            firstQuote + 1
                    );

            if (secondQuote == -1) {
                return null;
            }

            return text.substring(
                    firstQuote + 1,
                    secondQuote
            );

        } catch (Exception ignored) {
        }

        return null;
    }

    // =========================================================
    // UPDATE SIGNAL COLOR
    // =========================================================

    private void updateSignal(
            JLabel label,
            String signal
    ) {

        String value =
                signal.toUpperCase();

        if (
                value.contains(
                        "GREEN"
                )
        ) {

            label.setText(
                    "● GREEN"
            );

            label.setForeground(
                    new Color(
                            0,
                            150,
                            0
                    )
            );

        } else if (
                value.contains(
                        "RED"
                )
        ) {

            label.setText(
                    "● RED"
            );

            label.setForeground(
                    Color.RED
            );

        } else if (
                value.contains(
                        "YELLOW"
                )
        ) {

            label.setText(
                    "● YELLOW"
            );

            label.setForeground(
                    new Color(
                            220,
                            160,
                            0
                    )
            );

        } else {

            label.setText(
                    "● " +
                            value
            );

            label.setForeground(
                    Color.GRAY
            );
        }
    }

    // =========================================================
    // GENERIC API CALL
    // =========================================================

    private void callAPI(
            String endpoint,
            String title
    ) {

        details.setText(
                "========== " +
                        title +
                        " ==========\n\n" +
                        "Loading..."
        );

        new Thread(
                () -> {

                    try {

                        String json =
                                getAPI(
                                        endpoint
                                );

                        SwingUtilities.invokeLater(
                                () -> {

                                    details.setText(
                                            "========== " +
                                                    title +
                                                    " ==========\n\n" +
                                                    formatJSON(
                                                            json
                                                    )
                                    );
                                }
                        );

                    } catch (Exception e) {

                        SwingUtilities.invokeLater(
                                () -> {

                                    details.setText(
                                            "ERROR CONNECTING TO BACKEND\n\n"
                                                    +
                                                    e.getMessage()
                                    );
                                }
                        );
                    }

                }
        ).start();
    }

    // =========================================================
    // HTTP GET
    // =========================================================

    private String getAPI(
            String endpoint
    ) throws Exception {

        HttpClient client =
                HttpClient.newHttpClient();

        HttpRequest request =
                HttpRequest.newBuilder()
                        .uri(
                                URI.create(
                                        API +
                                                endpoint
                                )
                        )
                        .GET()
                        .build();

        HttpResponse<String> response =
                client.send(
                        request,
                        HttpResponse.BodyHandlers.ofString()
                );

        if (
                response.statusCode() < 200
                        ||
                response.statusCode() >= 300
        ) {

            throw new Exception(
                    "HTTP ERROR: " +
                            response.statusCode()
            );
        }

        return response.body();
    }

    // =========================================================
    // SIMPLE JSON FORMATTING
    // =========================================================

    private String formatJSON(
            String json
    ) {

        return json
                .replace(
                        "{",
                        "{\n"
                )
                .replace(
                        "}",
                        "\n}"
                )
                .replace(
                        ",",
                        ",\n"
                )
                .replace(
                        ":",
                        " : "
                );
    }

    // =========================================================
    // MAIN
    // =========================================================

    public static void main(
            String[] args
    ) {

        SwingUtilities.invokeLater(
                () -> {

                    TrafficDashboard dashboard =
                            new TrafficDashboard();

                    dashboard.setVisible(
                            true
                    );
                }
        );
    }
}