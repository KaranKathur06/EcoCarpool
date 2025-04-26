<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

include_once '../config/database.php';

try {
    $database = new Database();
    $db = $database->getConnection();

    // Get total users
    $query = "SELECT COUNT(*) as total FROM users";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $totalUsers = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    // Get total rides
    $query = "SELECT COUNT(*) as total FROM rides";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $totalRides = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    // Get total earnings
    $query = "SELECT SUM(amount) as total FROM transactions WHERE type = 'earning'";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $totalEarnings = $stmt->fetch(PDO::FETCH_ASSOC)['total'] ?? 0;

    // Get total expenses
    $query = "SELECT SUM(amount) as total FROM transactions WHERE type = 'expense'";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $totalExpenses = $stmt->fetch(PDO::FETCH_ASSOC)['total'] ?? 0;

    // Get total passengers
    $query = "SELECT COUNT(DISTINCT passenger_id) as total FROM ride_passengers";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $totalPassengers = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    // Get monthly earnings (last 6 months)
    $query = "SELECT 
                MONTH(created_at) as month,
                SUM(amount) as amount
              FROM transactions 
              WHERE type = 'earning'
              AND created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
              GROUP BY MONTH(created_at)
              ORDER BY month";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $monthlyEarnings = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Get weekly rides
    $query = "SELECT 
                DAYNAME(created_at) as day,
                COUNT(*) as count
              FROM rides
              WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
              GROUP BY DAYNAME(created_at)
              ORDER BY DAYOFWEEK(created_at)";
    $stmt = $db->prepare($query);
    $stmt->execute();
    $weeklyRides = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Prepare response
    $response = [
        'totalUsers' => (int)$totalUsers,
        'totalRides' => (int)$totalRides,
        'totalEarnings' => (float)$totalEarnings,
        'totalExpenses' => (float)$totalExpenses,
        'totalPassengers' => (int)$totalPassengers,
        'monthlyEarnings' => $monthlyEarnings,
        'weeklyRides' => $weeklyRides
    ];

    echo json_encode($response);

} catch(PDOException $e) {
    echo json_encode([
        'error' => $e->getMessage()
    ]);
}
?> 