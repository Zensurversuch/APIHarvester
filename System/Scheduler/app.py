from flask import Flask, request, jsonify
import configparser
import logging
import docker

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dockerClient = docker.from_env()

CONFIG_FILE = '/app/opheliaConfig/config.ini'


@app.route('/hello')
def hello():
    return 'Hello, World from Scheduler!'

@app.route('/addJob', methods=['POST'])
def addJob():
    data = request.json
    jobName = data.get('jobName')
    schedule = data.get('schedule')
    command = data.get('command')
    container = data.get('container', '')
    image = data.get('image', '')

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    sectionName = f'job-exec "{jobName}"'
    if sectionName not in config:
        config.add_section(sectionName)

    config[sectionName]['schedule'] = schedule
    config[sectionName]['command'] = command
    if container:
        config[sectionName]['container'] = container
    if image:
        config[sectionName]['image'] = image

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    refreshOfelia()
    return jsonify({"message": "Job added"}), 200

@app.route('/deleteJob', methods=['POST'])
def deleteJob():
    data = request.json
    jobName = data.get('jobName')

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    section_name = f'job-exec "{jobName}"'
    if section_name in config:
        config.remove_section(section_name)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        refreshOfelia()
        return jsonify({"message": "Job deleted"}), 200
    else:
        return jsonify({"message": "Job not found"}), 404

def refreshOfelia():
    try:
        container = dockerClient.containers.get('ofelia')
        container.restart()
        container.reload
        logger.info("Ofelia container has been restarted successfully.")
        return "Ofelia container has been restarted successfully."
    except docker.errors.NotFound:
        logger.error("Ofelia container not found.")
        return "Ofelia container not found."
    except docker.errors.APIError as e:
        logger.error(f"Error restarting Ofelia container: {str(e)}")
        return f"Error restarting Ofelia container: {str(e)}"

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000, debug=True)