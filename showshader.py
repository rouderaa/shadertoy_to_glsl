import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import time
import traceback  # For detailed traceback
import argparse

# Function to load the shader source code from a file
def load_shader_source(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading shader from file {file_path}: {e}")
        traceback.print_exc()
        exit(1)


# Function to get the compilation log for a shader
def get_shader_log(shader):
    log_length = glGetShaderiv(shader, GL_INFO_LOG_LENGTH)
    log = glGetShaderInfoLog(shader, log_length).decode('utf-8')
    return log


# Function to create a full-screen quad (two triangles that cover the screen)
def create_fullscreen_quad():
    try:
        quad_vertices = np.array([
            -1.0, -1.0, 0.0,
            1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
        ], dtype=np.float32)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        return vao
    except Exception as e:
        print(f"Error creating fullscreen quad: {e}")
        traceback.print_exc()
        exit(1)


# Function to compile and link the shaders into an OpenGL program
def create_shader_program(fragment_shader_source):
    vertex_shader_source = """
    #version 330 core
    layout(location = 0) in vec3 inPosition;

    void main() {
        gl_Position = vec4(inPosition, 1.0);
    }
    """

    try:
        print("Compiling vertex shader...")
        vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
        print("Vertex shader compiled successfully.")
    except RuntimeError as e:
        print(f"Vertex shader compilation failed:\n{e}")
        print(f"Shader log:\n{get_shader_log(vertex_shader)}")  # Print shader log
        traceback.print_exc()
        exit(1)

    try:
        print("Compiling fragment shader...")
        fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
        print("Fragment shader compiled successfully.")
    except RuntimeError as e:
        print(f"Fragment shader compilation failed:\n{e}")
        print(f"Shader log:\n{get_shader_log(fragment_shader)}")  # Print shader log
        traceback.print_exc()
        exit(1)

    try:
        print("Linking shaders into a program...")
        shader_program = compileProgram(vertex_shader, fragment_shader)
        print("Shader program linked successfully.")
    except RuntimeError as e:
        print(f"Shader program linking failed:\n{e}")
        traceback.print_exc()
        exit(1)

    return shader_program


# Function to check for OpenGL errors
def check_opengl_errors():
    error = glGetError()
    if error != GL_NO_ERROR:
        error_message = {
            GL_NO_ERROR: "No error",
            GL_INVALID_ENUM: "Invalid enum",
            GL_INVALID_VALUE: "Invalid value",
            GL_INVALID_OPERATION: "Invalid operation",
            GL_OUT_OF_MEMORY: "Out of memory",
        }.get(error, "Unknown error")
        print(f"OpenGL error occurred: {error} - {error_message}")
        traceback.print_stack()
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="A program to display a shader using OpenGL.")
    parser.add_argument("shaderfile", help="The fragment shader file to display.")

    args = parser.parse_args()

    try:
        # Initialize Pygame and create a window with OpenGL context
        pygame.init()
        screen_size = (800, 600)
        pygame.display.set_mode(screen_size, pygame.OPENGL | pygame.DOUBLEBUF)

        # Set OpenGL clear color (background color)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        check_opengl_errors()

        # Check OpenGL version
        info = glGetString(GL_VERSION)
        if not info:
            raise RuntimeError("Unable to get OpenGL version")
        print(f"OpenGL Version: {info.decode()}")

        # Load fragment shader from a file

        fragment_shader_file = args.shaderfile
        fragment_shader_source = load_shader_source(fragment_shader_file)

        # Compile and link shaders into a program
        shader_program = create_shader_program(fragment_shader_source)

        # Create a full-screen quad
        vao = create_fullscreen_quad()

        # Set up uniforms
        resolution_location = glGetUniformLocation(shader_program, "uResolution")
        if resolution_location == -1:
            print("Warning: 'uResolution' uniform not found in shader.")
        time_location = glGetUniformLocation(shader_program, "uTime")  # For uTime uniform
        if time_location == -1:
            print("Warning: 'uTime' uniform not found in shader.")

        glUseProgram(shader_program)  # Use the shader program to set uniforms
        glUniform2f(resolution_location, screen_size[0], screen_size[1])
        check_opengl_errors()

        start_time = time.time()  # Record the start time for uTime calculation

        # Main render loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Calculate elapsed time
            current_time = time.time() - start_time

            # Clear the screen
            glClear(GL_COLOR_BUFFER_BIT)
            check_opengl_errors()

            # Use the shader program
            glUseProgram(shader_program)

            # Update time uniform
            glUniform1f(time_location, current_time)

            # Draw the full-screen quad
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
            check_opengl_errors()  # Check for errors after drawing
            glBindVertexArray(0)

            # Swap the display buffers (double buffering)
            pygame.display.flip()

        # Cleanup and exit
        glDeleteVertexArrays(1, [vao])
        glDeleteProgram(shader_program)
        pygame.quit()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        pygame.quit()
        exit(1)


if __name__ == "__main__":
    main()
