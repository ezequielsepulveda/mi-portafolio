<?php
session_start();
if (!isset($_SESSION['username'])) {
    header("Location: index.html");
}

$host = "localhost";
$username = "root";
$password = "";
$database = "loginsing";
$port = 3307;

$conn = mysqli_connect($host, $username, $password, $database, $port);
if (!$conn) {
    die("Error al conectar con la base de datos: " . mysqli_connect_error());
}

$username = $_SESSION['username'];

$query = "SELECT * FROM users WHERE username='$username'";
$result = mysqli_query($conn, $query);
$row = mysqli_fetch_assoc($result);

$bmi = $row['bmi'];
$category = $row['category'];

mysqli_close($conn);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="css/perfil.css">
    <title>PERFIL USUARIO</title>
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

    <section >
        <div>
        <h2>Perfil de usuario</h2>
        </div>  
    <div class="container">
        <div class="card">
            <img src="img/perfil.jpg" alt="Perfil">
            <div class="intro">
            <h4> <?php echo $username; ?></h4>
            <p><strong>Edad:</strong> <?php echo $row['age']; ?></p>
            <p><strong>Peso:</strong> <?php echo $row['weight']; ?> kg</p>
            <p><strong>Estatura:</strong> <?php echo $row['height']; ?> cm</p>
            <p><strong>IMC:</strong> <?php echo $bmi; ?> (<?php echo $category; ?>)</p>

            </div>
            
        </div>
        <a  href="edit_perfil.php">Editar perfil</a> 
        <br>
        <a href="logout.php">Cerrar sesión</a>
    </div>        
        

    </section>

    
</body>
</html>