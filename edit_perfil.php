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

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
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

    $query = "UPDATE users SET weight='$weight', height='$height', bmi='$bmi', category='$category' 
            WHERE username='$username'";

    if (mysqli_query($conn, $query)) {
        echo "Perfil actualizado correctamente. <a href='perfil.php'>Volver al perfil</a>";
    } else {
        echo "Error al actualizar el perfil: " . mysqli_error($conn);
    }
}

mysqli_close($conn);
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="css/edit_perfil.css">

    <title>Editar Perfil</title>
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
    
    <form class="form-edit">
        <h2 style="text-align: center;">Editar perfil</h2>
        <input class="controls" type="number" name="weight" placeholder="Peso" step="0.01" required><br><br>
        <input class="controls" type="number" name="height" placeholder="Estatura" step="0.01" required><br><br>
        <input class="controls" type="submit" value="Guardar cambios">
        
        <p><a href="perfil.php">Volver</a></p>
        <p><a href="login.html">Cancelar</a></p>
    </form>
    
    </section>
    
</body>
</html>