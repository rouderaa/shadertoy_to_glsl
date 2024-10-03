import re
import argparse

def convert_shadertoy_to_glsl(shadertoy_shader):
    """
    Converts a ShaderToy shader to a GLSL shader suitable for OpenGL.
    """
    # Replace ShaderToy variables with OpenGL equivalents
    glsl_shader = shadertoy_shader

    # Replace `iResolution` with a uniform vec2
    glsl_shader = re.sub(r'\biResolution\b', 'uResolution', glsl_shader)

    # Replace `iTime` with a uniform float
    glsl_shader = re.sub(r'\biTime\b', 'uTime', glsl_shader)

    # Replace `void mainImage` with `void main()`
    glsl_shader = re.sub(r'void mainImage\( out vec4 fragColor, in vec2 fragCoord \)', 'void main()', glsl_shader)

    # Replace `fragCoord` with `gl_FragCoord.xy`
    glsl_shader = re.sub(r'\bfragCoord\b', 'gl_FragCoord.xy', glsl_shader)

    # Add version and uniform definitions at the beginning
    header = '''#version 330 core
uniform float uTime;         // Equivalent to iTime
uniform vec2 uResolution;    // Equivalent to iResolution
out vec4 fragColor;          // Output variable
'''
    glsl_shader = header + glsl_shader

    return glsl_shader

def read_shader_from_file(file_path):
    """Reads the shader from the input file."""
    with open(file_path, 'r') as file:
        return file.read()

def write_shader_to_file(file_path, shader_code):
    """Writes the converted GLSL shader to the output file."""
    with open(file_path, 'w') as file:
        file.write(shader_code)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="A program to convert shadertoy.com shaders to GLSL shaders for OpenGL.")
    parser.add_argument("input_file", help="The name of the shadertoy.com shader file to convert")
    parser.add_argument("output_file", help="The name of the glsl shader file to write to")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # Read the ShaderToy shader from the input file
    shadertoy_shader = read_shader_from_file(input_file)

    # Convert the ShaderToy shader to GLSL
    glsl_shader = convert_shadertoy_to_glsl(shadertoy_shader)

    # Write the converted GLSL shader to the output file
    write_shader_to_file(output_file, glsl_shader)

    print(f"Converted shader written to {output_file}")

if __name__ == "__main__":
    main()
