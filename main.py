from flask import Flask, request, send_file
import os
import subprocess
import tempfile
import uuid

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        # Get the Manim code from the request
        data = request.get_json()
        manim_code = data.get('code')

        if not manim_code:
            return "No Manim code provided", 400

        # Replace newline escape sequences (\n) with actual newlines
        manim_code = manim_code.replace(r'\n', '\n')

        # Create a temporary directory to store the generated scene file
        temp_dir = tempfile.mkdtemp()
        script_filename = f"script_{uuid.uuid4().hex}.py"
        script_filepath = os.path.join(temp_dir, script_filename)

        # Write the Manim code to the script file
        with open(script_filepath, 'w') as f:
            f.write(manim_code)

        # Command to run Manim and generate the video (without '-p' to prevent opening the file)
        output_dir = os.path.join(temp_dir, 'media', 'videos')
        os.makedirs(output_dir, exist_ok=True)

        output_filepath = os.path.join(output_dir, f"{uuid.uuid4().hex}.mp4")

        command = [
            "manim",
            "-ql",  # Low quality (optional)
            "--output_file", output_filepath,
            script_filepath
        ]

        # Capture the standard output and error of the command for debugging
        result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Debug: print Manim command output
        print(f"Manim command output: {result.stdout}")
        print(f"Manim command error: {result.stderr}")

        # If the command failed, return the error
        if result.returncode != 0:
            return f"Manim failed with error: {result.stderr}", 500

        # Make sure the output file path is absolute
        output_filepath = os.path.abspath(output_filepath)

        # Debug print: Confirm absolute path
        print(f"Absolute path: {output_filepath}")

        # Ensure the file exists before sending
        if os.path.exists(output_filepath):
            return send_file(output_filepath, as_attachment=True, download_name="rendered_video.mp4")

        return "Video generation failed", 500

    except Exception as e:
        # Print the error for debugging
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
