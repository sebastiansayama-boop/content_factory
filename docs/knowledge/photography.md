# Photography: physical and photographic principles

Status: reusable domain knowledge. Scope: still photography and image-generation realism; not a camera simulation or guaranteed model behavior.

## Image formation
A photographed image depends on illumination, scene geometry and materials, optics/perspective, exposure/sensor response, and processing. Image generators can imitate the result without enforcing all physical constraints.

## Light
- Direction affects highlights, shading and cast-shadow orientation.
- Apparent angular size of a light source controls shadow softness: larger apparent sources generally produce softer transitions.
- Light can be direct, reflected (fill) or transmitted; room surfaces contribute to illumination.
- Light intensity, distance, spectral distribution and white balance influence exposure and color. Inverse-square falloff is a useful approximation for point-like sources, not a universal rule for windows or complex rooms.
- Multiple lights and reflections mean a single image need not have one obvious shadow direction.

## Shadows and materials
- Form shadow: surface turned away from illumination. Cast shadow: light blocked onto another surface. Contact/occlusion shadow: reduced illumination at close interfaces.
- Shadows should be compatible with scene geometry, light size and direction, while allowing fill/reflections.
- Skin has spatially varying texture, specular response and subsurface scattering. Hair, fabric, glass and metal respond differently; uniform 'pore texture' is not a substitute for realistic skin.
- Check object interaction (hand/cup/table), not just facial appearance.

## Camera and capture
- Perspective depends on camera position and subject distance; focal length sets field of view, and affects perspective indirectly when reframing from a different distance.
- Aperture, focal length, focus distance and sensor format jointly affect depth of field.
- Shutter time affects motion blur; ISO/gain affects brightness/noise tradeoffs; dynamic range and tone mapping affect highlight and shadow detail.
- Phone images may use computational photography (HDR, denoising, sharpening and portrait segmentation). 'Phone photo' is not synonymous with noisy or blurry.
- Lighting, framing and processing can legitimately look polished; perfection is a warning only when repeated implausibly across everyday scenes.

## Realism checks
1. Can the described camera position produce this perspective?
2. Are illumination, cast shadows, occlusion and reflections mutually plausible?
3. Do skin/hair/clothing and objects respond coherently to the same environment?
4. Does exposure/blur/depth of field match the purported capture method?
5. Is the person's behavior natural for the task, rather than consistently posing?
6. Is identity consistent across outputs? Assess separately from photographic realism.

## Limitations
A single image rarely proves lighting geometry, authenticity, camera metadata or identity. These are visual plausibility checks, not forensic authentication. Do not manufacture grain, blemishes or camera defects to imitate reality.
