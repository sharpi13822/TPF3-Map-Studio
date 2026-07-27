from collections import defaultdict


class RingAssembler:
    """
    Fügt Way-Segmente zu geschlossenen Ringen zusammen.
    """

    def assemble(self, segments):

        if not segments:
            return []

        endpoint_index = defaultdict(list)

        for index, segment in enumerate(segments):

            if len(segment) < 2:
                continue

            endpoint_index[segment[0]].append(index)
            endpoint_index[segment[-1]].append(index)

        used = set()
        rings = []

        for start_index, start_segment in enumerate(segments):

            if start_index in used:
                continue

            if len(start_segment) < 2:
                continue

            ring = list(start_segment)
            current_used = {start_index}

            while True:

                #
                # Ring geschlossen
                #
                if len(ring) >= 4 and ring[0] == ring[-1]:
                    rings.append(ring)
                    used.update(current_used)
                    break

                start = ring[0]
                end = ring[-1]

                found = False

                #
                # Ende -> Anfang
                # Ende -> Ende
                #
                for segment_index in endpoint_index[end]:

                    if segment_index in current_used:
                        continue

                    segment = segments[segment_index]

                    if len(segment) < 2:
                        continue

                    if segment[0] == end:

                        ring.extend(segment[1:])
                        current_used.add(segment_index)
                        found = True
                        break

                    if segment[-1] == end:

                        ring.extend(reversed(segment[:-1]))
                        current_used.add(segment_index)
                        found = True
                        break

                if found:
                    continue

                #
                # Anfang -> Ende
                # Anfang -> Anfang
                #
                for segment_index in endpoint_index[start]:

                    if segment_index in current_used:
                        continue

                    segment = segments[segment_index]

                    if len(segment) < 2:
                        continue

                    if segment[-1] == start:

                        ring = segment[:-1] + ring
                        current_used.add(segment_index)
                        found = True
                        break

                    if segment[0] == start:

                        ring = list(reversed(segment[1:])) + ring
                        current_used.add(segment_index)
                        found = True
                        break

                if not found:
                    break

        return rings