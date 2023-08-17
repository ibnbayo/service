from rest_framework import serializers

class ForecastSerializer(serializers.Serializer):

    clouds = serializers.CharField(max_length=20)
    humidity = serializers.CharField(max_length=10)
    pressure = serializers.CharField(max_length=10) 
    temperature = serializers.CharField(max_length=10)

    def validate(self, data):
        """Validate weather data."""
        if 'main' in data:
            humidity = data['main'].get('humidity')
            if humidity and int(humidity) > 100: 
                raise serializers.ValidationError("Invalid humidity")
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'weather' in instance:
            data['clouds'] = instance['weather'][0]['description']
        if 'main' in instance:
            data['humidity'] = str(instance['main']['humidity']) + '%'
            data['pressure'] = str(round(instance['main']['pressure'] / 10)) + ' hPa'
            data['temperature'] = str(round(instance['main']['temp'])) + '°C'
        return data