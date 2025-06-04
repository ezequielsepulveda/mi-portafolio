import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, date
from django.utils import timezone
import joblib
import os

class PriorityMLSystem:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = 'ml_models/priority_model.joblib'
        self.scaler_path = 'ml_models/scaler.joblib'
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Inicializar scaler con datos básicos si no existe
        if not self.load_model():
            # Datos de ejemplo para el scaler
            sample_data = np.array([
                [0.5, 0.5, 0.5, 0.5, 0.5],  # Valores medios
                [0.1, 0.1, 0.0, 0.1, 1.0],  # Valores mínimos
                [1.0, 1.0, 1.0, 1.0, 0.0]   # Valores máximos
            ])
            self.scaler.fit(sample_data)
            self.save_model()

    def preparar_features(self, paciente):
        """Prepara las características del paciente para el modelo ML"""
        try:
            features = []
            
            # Edad normalizada (0-1)
            edad = (date.today() - paciente.fecha_nacimiento).days / 365.25
            edad_normalizada = min(edad / 100, 1)
            features.append(edad_normalizada)
            
            # Prioridad base del diagnóstico
            prioridad_base = paciente.diagnostico.prioridad_base if paciente.diagnostico else 0.5
            features.append(prioridad_base)
            
            # Género codificado
            genero_map = {'M': 1, 'F': 0, 'O': 0.5}
            genero_cod = genero_map.get(paciente.genero, 0.5)
            features.append(genero_cod)
            
            # Tiempo en lista de espera (días)
            now = timezone.now()
            fecha_registro = paciente.fecha_registro
            
            if hasattr(fecha_registro, 'tzinfo') and fecha_registro.tzinfo is None:
                fecha_registro = timezone.make_aware(fecha_registro)
            
            dias_espera = (now - fecha_registro).days
            tiempo_espera_norm = min(dias_espera / 365, 1)
            features.append(tiempo_espera_norm)
            
            # Historial de citas
            citas_totales = paciente.cita_set.count()
            citas_perdidas = paciente.cita_set.filter(estado='N').count()
            tasa_asistencia = 1 - (citas_perdidas / max(citas_totales, 1))
            features.append(tasa_asistencia)

            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"Error preparando features: {e}")
            return np.array([0.5, 0.5, 0.5, 0.5, 0.5]).reshape(1, -1)

    def predecir_prioridad(self, paciente):
        """Predice la prioridad para un paciente"""
        try:
            features = self.preparar_features(paciente)
            
            # Usar cálculo base si no hay modelo o scaler
            if not hasattr(self, 'model') or not hasattr(self, 'scaler'):
                return self.calcular_prioridad_base(paciente)
            
            # Normalizar características
            features_scaled = self.scaler.transform(features)
            prediccion = self.calcular_prioridad_base(paciente)  # Valor por defecto
            
            try:
                prediccion = self.model.predict(features_scaled)[0]
            except Exception as e:
                print(f"Error en predicción del modelo: {e}")
            
            # Ajustar por edad
            edad = paciente.calcular_edad()
            if edad < 18:
                prediccion *= 1.2
            elif edad > 60:
                prediccion *= 1.3
            
            return max(0, min(1, prediccion))
            
        except Exception as e:
            print(f"Error en predicción ML: {e}")
            return self.calcular_prioridad_base(paciente)

    def calcular_prioridad_base(self, paciente):
        """Cálculo básico de prioridad"""
        try:
            prioridad_base = paciente.diagnostico.prioridad_base if paciente.diagnostico else 0.5
            edad = paciente.calcular_edad()
            
            if edad < 18:
                prioridad_base *= 1.2
            elif edad > 60:
                prioridad_base *= 1.3
            
            return min(prioridad_base, 1.0)
            
        except Exception as e:
            print(f"Error en cálculo base: {e}")
            return 0.5

    def save_model(self):
        """Guarda el modelo y el scaler"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            return True
        except Exception as e:
            print(f"Error guardando modelo: {e}")
            return False

    def load_model(self):
        """Carga el modelo y el scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
        except Exception as e:
            print(f"Error cargando modelo ML: {e}")
        return False