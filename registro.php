<?php
$host = "localhost";
$username = "root";
$password = "";
$database = "loginsing";
$port = 3307;

$conn = mysqli_connect($host, $username, $password, $database, $port);
if (!$conn) {
    die("Error al conectar con la base de datos: " . mysqli_connect_error());
}

$username = $_POST['username'];
$password = password_hash($_POST['password'], PASSWORD_DEFAULT);
$age = $_POST['age'];
$weight = $_POST['weight'];
$height = $_POST['height'];
$bmi = $weight / (($height / 100) ** 2);

if ($bmi < 18.5) {
    $category = "Bajo peso";
} elseif ($bmi >= 18.5 && $bmi < 25) {
    $category = "Peso normal";
} elseif ($bmi >= 25 && $bmi < 30) {
    $category = "Sobrepeso";
} else {
    $category = "Obesidad";
}

$query = "INSERT INTO users (username, password, age, weight, height, bmi, category) 
        VALUES ('$username', '$password', '$age', '$weight', '$height', '$bmi', '$category')";

if (mysqli_query($conn, $query)) {
    echo "Registro exitoso. <a href='login.html'>Iniciar sesión</a>";
} else {
    echo "Error al registrar: " . mysqli_error($conn);
}

mysqli_close($conn);
?>