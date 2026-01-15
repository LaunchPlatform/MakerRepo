"use strict";

(function () {
    const MAP_HEX = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        a: 10,
        b: 11,
        c: 12,
        d: 13,
        e: 14,
        f: 15,
        A: 10,
        B: 11,
        C: 12,
        D: 13,
        E: 14,
        F: 15
    };

    function debugLog(tag, obj) {
        console.log(tag, obj);
    }

    function fromHex(hexString) {
        const bytes = new Uint8Array(
            Math.floor((hexString || "").length / 2)
        );
        let i;
        for (i = 0; i < bytes.length; i++) {
            const a = MAP_HEX[hexString[i * 2]];
            const b = MAP_HEX[hexString[i * 2 + 1]];
            if (a === undefined || b === undefined) {
                break;
            }
            bytes[i] = (a << 4) | b;
        }
        return i === bytes.length ? bytes : bytes.slice(0, i);
    }

    function fromB64(s) {
        const bytes = atob(s);
        const uint = new Uint8Array(bytes.length);
        for (let i = 0; i < bytes.length; i++) {
            uint[i] = bytes[i].charCodeAt(0);
        }
        return uint;
    }

    function convert(obj) {
        let result;
        if (typeof obj.buffer === "string") {
            let buffer;
            if (obj.codec === "b64") {
                buffer = fromB64(obj.buffer);
            } else {
                buffer = fromHex(obj.buffer);
            }
            if (obj.dtype === "float32") {
                result = new Float32Array(buffer.buffer);
            } else if (obj.dtype === "int32") {
                result = new Uint32Array(buffer.buffer);
            } else if (obj.dtype === "uint32") {
                result = new Uint32Array(buffer.buffer);
            } else {
                debugLog("Error: unknown dtype", obj.dtype);
            }
        } else if (Array.isArray(obj)) {
            result = [];
            for (const arr of obj) {
                result.push(convert(arr));
            }
            return result;
        } else {
            debugLog("Error: unknown buffer type", obj.buffer);
        }
        return result;
    }

    function walk(obj, instances) {
        let type = null;
        for (const attr in obj) {
            if (attr === "parts") {
                for (const i in obj.parts) {
                    walk(obj.parts[i], instances);
                }
            } else if (attr === "type") {
                type = obj.type;
            } else if (attr === "shape") {
                if (type === "shapes") {
                    if (obj.shape.ref === undefined) {
                        obj.shape.vertices = convert(
                            obj.shape.vertices
                        );
                        obj.shape.obj_vertices = convert(
                            obj.shape.obj_vertices
                        );
                        obj.shape.normals = convert(
                            obj.shape.normals
                        );
                        obj.shape.edge_types = convert(
                            obj.shape.edge_types
                        );
                        obj.shape.face_types = convert(
                            obj.shape.face_types
                        );
                        obj.shape.triangles = convert(
                            obj.shape.triangles
                        );
                        obj.shape.triangles_per_face = convert(
                            obj.shape.triangles_per_face
                        );
                        obj.shape.edges = convert(obj.shape.edges);
                        obj.shape.segments_per_edge = convert(
                            obj.shape.segments_per_edge
                        );
                    } else {
                        const ind = obj.shape.ref;
                        if (ind !== undefined && instances !== undefined) {
                            obj.shape = instances[ind];
                        }
                    }
                } else if (type === "edges") {
                    obj.shape.edges = convert(obj.shape.edges);
                    if (obj.shape.edges === undefined) {
                        obj.shape.edges = [];
                    }
                    obj.shape.segments_per_edge = convert(
                        obj.shape.segments_per_edge
                    );
                    obj.shape.obj_vertices = convert(
                        obj.shape.obj_vertices
                    );
                } else {
                    obj.shape.obj_vertices = convert(
                        obj.shape.obj_vertices
                    );
                }
            }
        }
    }

    function decode(model) {
        model.instances.forEach((instance) => {
            instance.vertices = convert(instance.vertices);
            instance.obj_vertices = convert(instance.obj_vertices);
            instance.normals = convert(instance.normals);
            instance.edge_types = convert(instance.edge_types);
            instance.face_types = convert(instance.face_types);
            instance.triangles = convert(instance.triangles);
            instance.triangles_per_face = convert(
                instance.triangles_per_face
            );
            instance.edges = convert(instance.edges);
            instance.segments_per_edge = convert(
                instance.segments_per_edge
            );
        });

        walk(model.shapes, model.instances);
        model.instances = [];
    }

    // Expose walk function via namespace
    window.CadUtils = {
        decode
    };
})();
