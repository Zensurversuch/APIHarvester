from flask import Flask, jsonify, request
import docker

app = Flask(__name__)
client = docker.from_env()

CLI_CONTAINER_NAME = 'cli'  # Name des CLI-Containers aus docker-compose ps

@app.route('/scale/<int:num_instances>', methods=['GET'])
def scale_redis_workers(num_instances):
    try:
        command = f"docker-compose up -d --no-recreate --scale redis_worker={num_instances}"

        # Befehl an den CLI-Container senden
        cli_container = client.containers.get(CLI_CONTAINER_NAME)
        exec_command = cli_container.exec_run(command, detach=True)

        # Debugging Ausgabe
        print(f"Executed command '{command}' in container '{CLI_CONTAINER_NAME}'")
        print(f"Command execution result: {exec_command}")

        return jsonify({'message': 'Command successfully sent to CLI container.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
