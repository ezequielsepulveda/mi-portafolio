<?php
session_start();
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
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username='$username'";
$result = mysqli_query($conn, $query);
$row = mysqli_fetch_assoc($result);

if (mysqli_num_rows($result) == 1) {
    if (password_verify($password, $row['password'])) {
        $_SESSION['username'] = $username;
        header("Location: perfil.php");
    }  else {
        echo "";
    }
} else {
    echo "";
}

mysqli_close($conn);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/login_error.css">
    <link rel="stylesheet" href="css/styles.css">
    <title>incorrecto</title>
</head>
<body>
<header class="header">
        <a href="index.html" class="logo">
            <i class="fas fa-dumbbell"></i>FitHome
        </a>
        <nav class="navbar">
            <a href="index.html">Inicio</a>
            <a href="iniciar.html">Entrenamiento</a>
            <a href="membresia.html">Membresia</a>
            <a href="login.html" class="btn">Login</a>
            <a href="registro.html" class="btn">Sign Up</a>
        </nav>
    </header>
    <section class="login-error">
        <form>
        <h2 style="text-align: center;">Vuelve a Intentar</h2>
        <br>
        <p>Nombre de usuario o contraseña incorrectos. <a href='login.html' > <br> al inicio de sesión</a></p>
        
        </form>

</section>
    
    
</body>
</html>