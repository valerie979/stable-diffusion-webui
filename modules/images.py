def read_info_from_image(image: Image.Image) -> tuple[str | None, dict]:
    items = (image.info or {}).copy()

    geninfo = items.pop('parameters', None)

    if "exif" in items:
        try:
            exif = piexif.load(items["exif"])
            exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
            try:
                exif_comment = piexif.helper.UserComment.load(exif_comment)
            except ValueError:
                exif_comment = exif_comment.decode('utf8', errors="ignore")

            if exif_comment:
                items['exif comment'] = exif_comment
                geninfo = exif_comment
        except OSError as e:  # Catch OSError exceptions specifically
            # Fallback to empty EXIF data if there's an error
            items['exif'] = {}
            print(f"Error loading EXIF data: {e}")

    for field in IGNORED_INFO_KEYS:
        items.pop(field, None)

    if items.get("Software", None) == "NovelAI":
        try:
            json_info = json.loads(items["Comment"])
            sampler = sd_samplers.samplers_map.get(json_info["sampler"], "Euler a")

            geninfo = f"""{items["Description"]}
Negative prompt: {json_info["uc"]}
Steps: {json_info["steps"]}, Sampler: {sampler}, CFG scale: {json_info["scale"]}, Seed: {json_info["seed"]}, Size: {image.width}x{image.height}, Clip skip: 2, ENSD: 31337"""
        except Exception:
            errors.report("Error parsing NovelAI image generation parameters", exc_info=True)

    return geninfo, items