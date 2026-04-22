#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>

in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in float atmosphericHorizonBlend;

out vec4 fragColor;

void main() {
    float horizonRadius = clamp(ColorModulator.a, 0.25, 4.0);
    float gradientStrength = clamp(ModelOffset.x, 0.0, 2.0);
    float gradientT = gradientStrength * 0.5;
    float gradientShift = clamp(ModelOffset.y * 0.01, -1.0, 1.0);
    float horizonInput = clamp(atmosphericHorizonBlend + gradientShift, 0.0, 1.0);
    float edge0 = clamp(0.05 / horizonRadius, 0.0, 1.0);
    float edge1 = clamp(0.92 / horizonRadius, edge0 + 0.001, 1.0);
    float smoothBias = mix(0.24, 0.04, gradientT);
    edge0 = clamp(edge0 - smoothBias, 0.0, 1.0);
    edge1 = clamp(edge1 + smoothBias, edge0 + 0.001, 1.0);
    float horizonBlend = smoothstep(edge0, edge1, horizonInput);
    horizonBlend = pow(horizonBlend, mix(0.24, 0.78, gradientT));
    horizonBlend = clamp(horizonBlend * 2.6, 0.0, 1.0);
    vec4 atmosphericColor = vec4(mix(ColorModulator.rgb, FogColor.rgb, horizonBlend), 1.0);

    fragColor = apply_fog(atmosphericColor, sphericalVertexDistance, cylindricalVertexDistance, 0.0, FogSkyEnd, FogSkyEnd, FogSkyEnd, FogColor);
}
