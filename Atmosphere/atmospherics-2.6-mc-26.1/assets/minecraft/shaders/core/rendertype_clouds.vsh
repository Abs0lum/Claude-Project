#version 330

#moj_import <minecraft:mcsm.glsl>
#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>

const int FLAG_MASK_DIR = 7;
const int FLAG_INSIDE_FACE = 1 << 4;
const int FLAG_USE_TOP_COLOR = 1 << 5;
const int FLAG_EXTRA_Z = 1 << 6;
const int FLAG_EXTRA_X = 1 << 7;

layout(std140) uniform CloudInfo {
    vec4 CloudColor;
    vec3 CloudOffset;
    vec3 CellSize;
};

uniform isamplerBuffer CloudFaces;

out float vertexDistance;
out vec4 vertexColor;

const vec3[] vertices = vec3[](
    vec3(1, 0, 0), vec3(1, 0, 1), vec3(0, 0, 1), vec3(0, 0, 0),
    vec3(0, 1, 0), vec3(0, 1, 1), vec3(1, 1, 1), vec3(1, 1, 0),
    vec3(0, 0, 0), vec3(0, 1, 0), vec3(1, 1, 0), vec3(1, 0, 0),
    vec3(1, 0, 1), vec3(1, 1, 1), vec3(0, 1, 1), vec3(0, 0, 1),
    vec3(0, 0, 1), vec3(0, 1, 1), vec3(0, 1, 0), vec3(0, 0, 0),
    vec3(1, 0, 0), vec3(1, 1, 0), vec3(1, 1, 1), vec3(1, 0, 1)
);

const vec4[] faceColors = vec4[](
    vec4(0.7, 0.7, 0.7, 1.0),
    vec4(1.0, 1.0, 1.0, 1.0),
    vec4(0.8, 0.8, 0.8, 1.0),
    vec4(0.8, 0.8, 0.8, 1.0),
    vec4(0.9, 0.9, 0.9, 1.0),
    vec4(0.9, 0.9, 0.9, 1.0)
);

const float CloudFadeAlpha = 0.0;

float lerp(float d, float e, float f) {
    return e + d * (f - e);
}

float alphaByte(float alpha) {
    return clamp(floor(alpha * 255.0 + 0.5), 0.0, 255.0);
}

vec3 applyAtmosphericHaze(vec3 baseColor, vec3 worldPos, float fogDistance, float hazeStrength) {
    if (hazeStrength <= 0.001) {
        return baseColor;
    }

    vec3 viewPos = (ModelViewMat * vec4(worldPos, 1.0)).xyz;
    float horizontalDistance = length(viewPos.xz);
    float horizontalFactor = smoothstep(140.0, 420.0, horizontalDistance);
    float distanceFactor = smoothstep(0.0, 0.65, clamp(fogDistance / 160.0, 0.0, 1.0));
    float haze = clamp(horizontalFactor * mix(0.35, 1.0, distanceFactor) * hazeStrength, 0.0, 1.0);
    return mix(baseColor, FogColor.rgb, haze);
}

void main() {
    int quadVertex = gl_VertexID % 4;
    int index = (gl_VertexID / 4) * 3;

    int cellX = texelFetch(CloudFaces, index).r;
    int cellZ = texelFetch(CloudFaces, index + 1).r;
    int dirAndFlags = texelFetch(CloudFaces, index + 2).r;
    int direction = dirAndFlags & FLAG_MASK_DIR;
    bool isInsideFace = (dirAndFlags & FLAG_INSIDE_FACE) == FLAG_INSIDE_FACE;
    bool useTopColor = (dirAndFlags & FLAG_USE_TOP_COLOR) == FLAG_USE_TOP_COLOR;
    cellX = (cellX << 1) | ((dirAndFlags & FLAG_EXTRA_X) >> 7);
    cellZ = (cellZ << 1) | ((dirAndFlags & FLAG_EXTRA_Z) >> 6);

    vec3 faceVertex = vertices[(direction * 4) + (isInsideFace ? 3 - quadVertex : quadVertex)];

    float aByte = alphaByte(CloudColor.a);
    bool encodedVanilla = aByte >= 128.0 && aByte < 192.0;
    bool encodedStore = aByte >= 192.0 && aByte < 255.0;
    bool encoded = encodedVanilla || encodedStore;
    float rByte = clamp(floor(CloudColor.r * 255.0 + 0.5), 0.0, 255.0);
    float gByte = clamp(floor(CloudColor.g * 255.0 + 0.5), 0.0, 255.0);
    float bByte = clamp(floor(CloudColor.b * 255.0 + 0.5), 0.0, 255.0);
    float cellMetadata = floor(fract(CellSize.y) * 32768.0 + 0.5);
    float vanillaMetadata = mod(cellMetadata, 2048.0);
    float storeMetadata = encodedStore ? mod(cellMetadata, 2048.0) : 0.0;
    float visibilityIndex = encodedStore ? floor(cellMetadata / 2048.0) : mod(cellMetadata, 16.0);
    float cloudVisibility = encoded ? clamp(visibilityIndex / 15.0, 0.0, 1.0) : 1.0;
    bool vanillaShading = encodedVanilla ? floor(mod(vanillaMetadata / 16.0, 2.0)) > 0.5 : true;
    float distanceIndex = encodedVanilla ? floor(mod(aByte, 64.0) / 8.0) : (encodedStore ? mod(storeMetadata, 8.0) : 1.0);
    float distanceScale = max(0.001, distanceIndex / 7.0);
    bool storeMode = encodedStore;
    float hazeIndex = encodedVanilla ? floor(mod(vanillaMetadata / 32.0, 64.0)) : (encodedStore ? floor(mod(storeMetadata / 8.0, 16.0)) : 6.0);
    float hazeControl = encodedVanilla
        ? clamp(hazeIndex / 63.0, 0.0, 1.0)
        : clamp(hazeIndex / 15.0, 0.0, 1.0);
    float heightIndex = encodedStore
        ? floor(mod(storeMetadata / 128.0, 16.0))
        : floor((storyModeClouds_cloudHeight - 0.5) / 0.5 + 0.5);
    float CloudHeightStore = 0.5 + heightIndex * 0.5;
    float strongRange = smoothstep(0.10, 1.0, hazeControl);
    float hazeStrength = mix(hazeControl * 0.35, 1.35, strongRange);
    vec4 decodedCloudColor = CloudColor;
    if (storeMode) {
        decodedCloudColor.a = 1.0;
    }

    vec3 renderCellSize = vec3(CellSize.x, floor(CellSize.y), CellSize.z);

    if (!storeMode) {
        vec3 posVanilla = (faceVertex * renderCellSize) + (vec3(cellX, 0, cellZ) * renderCellSize) + CloudOffset;
        gl_Position = ProjMat * ModelViewMat * vec4(posVanilla, 1.0);
        vertexDistance = fog_spherical_distance(posVanilla) / distanceScale;
        vec4 shadeColor = vanillaShading ? (useTopColor ? faceColors[1] : faceColors[direction]) : vec4(1.0, 1.0, 1.0, 1.0);
        vec4 baseColor = shadeColor * decodedCloudColor;
        baseColor.rgb = applyAtmosphericHaze(baseColor.rgb, posVanilla, vertexDistance, hazeStrength);
        baseColor.a = cloudVisibility;
        vertexColor = baseColor;
        return;
    }

    vec3 scaledVertex = faceVertex * renderCellSize;
    scaledVertex.y *= CloudHeightStore;
    vec3 pos = scaledVertex + (vec3(cellX, 0, cellZ) * renderCellSize) + CloudOffset;

    gl_Position = ProjMat * ModelViewMat * vec4(pos, 1.0);
    vertexDistance = fog_spherical_distance(pos) / distanceScale;

    float brightness = 1.0;
    vec3 rgb = vec3(brightness);

    float baseA = encodedStore ? mod(aByte, 64.0) / 62.0 : floor(aByte / 2.0) * 2.0 / 255.0;
    float vertexY = pos.y - CloudOffset.y;
    float normalizedY = clamp(vertexY / CloudHeightStore, 0.0, 1.0);
    float dir = clamp(CloudOffset.y / CloudHeightStore, -1.0, 1.0);
    float fadeBelow = lerp(normalizedY, 1.0, CloudFadeAlpha);
    float fadeAbove = lerp(1.0 - normalizedY, 1.0, CloudFadeAlpha);
    float mixFactor = (dir + 1.0) * 0.5;
    float fade = mix(fadeBelow, fadeAbove, mixFactor);
    float finalA = baseA * (1 - fade) * cloudVisibility;

    vec4 baseColor = vec4(rgb, finalA) * decodedCloudColor;
    baseColor.rgb = applyAtmosphericHaze(baseColor.rgb, pos, vertexDistance, hazeStrength);
    vertexColor = baseColor;
}
