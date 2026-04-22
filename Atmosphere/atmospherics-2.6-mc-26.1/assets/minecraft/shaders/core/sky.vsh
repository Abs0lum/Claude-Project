#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>

in vec3 Position;

out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out float atmosphericHorizonBlend;

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);

    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);

    vec3 skyDirection = normalize(Position);
    float upperSkyFactor = smoothstep(0.16, 0.985, max(skyDirection.y, 0.0));
    float circleMask = 1.0 - smoothstep(0.70, 0.965, max(skyDirection.y, 0.0));
    atmosphericHorizonBlend = clamp((1.0 - upperSkyFactor) * circleMask, 0.0, 1.0);
}
