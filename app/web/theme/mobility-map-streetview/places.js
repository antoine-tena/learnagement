async function findPlaceByUniversity(university) {
    const placesService = new google.maps.places.PlacesService(document.createElement('div'));

    const findPlace = (query) => new Promise((resolve) => {
        placesService.findPlaceFromQuery(
            {
                query,
                fields: ['name', 'photos', 'formatted_address', 'place_id']
            },
            (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && results?.length) {
                    resolve({ places: results, status });
                    return;
                }
                resolve({ places: [], status });
            }
        );
    });

    const getDetails = (placeId) => new Promise((resolve) => {
        placesService.getDetails(
            {
                placeId,
                fields: ['name', 'photos', 'formatted_address', 'place_id']
            },
            (place, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && place) {
                    resolve({ place, status });
                    return;
                }
                resolve({ place: null, status });
            }
        );
    });

    const textSearch = (query, location) => new Promise((resolve) => {
        placesService.textSearch(
            {
                query,
                location,
                radius: 6000
            },
            (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && results?.length) {
                    resolve({ places: results, status });
                    return;
                }
                resolve({ places: [], status });
            }
        );
    });

    const photoMap = new Map();
    const statuses = [];

    const addPhotosFromPlace = (place) => {
        const photos = place?.photos || [];
        photos.forEach((photo) => {
            const thumbUrl = photo.getUrl({ maxWidth: 420, maxHeight: 260 });
            if (!photoMap.has(thumbUrl)) {
                photoMap.set(thumbUrl, {
                    thumbUrl,
                    fullUrl: photo.getUrl({ maxWidth: 1600, maxHeight: 1200 })
                });
            }
        });
    };

    const queries = [
        `${university.name} ${university.country}`,
        `${university.name} ${university.address}`,
        `${university.name} university`
    ];

    for (const query of queries) {
        const found = await findPlace(query);
        statuses.push(`findPlace:${found.status}`);
        for (const candidate of found.places.slice(0, 4)) {
            let place = candidate;
            if (place.place_id && (!place.photos || place.photos.length === 0)) {
                const details = await getDetails(place.place_id);
                statuses.push(`getDetails:${details.status}`);
                if (details.place) {
                    place = details.place;
                }
            }
            addPhotosFromPlace(place);
            if (photoMap.size >= 12) {
                return { photos: Array.from(photoMap.values()).slice(0, 12), status: statuses.join(' | ') };
            }
        }
    }

    const baseLocation = {
        lat: parseFloat(university.latitude),
        lng: parseFloat(university.longitude)
    };

    for (const query of queries) {
        const found = await textSearch(query, baseLocation);
        statuses.push(`textSearch:${found.status}`);
        for (const candidate of found.places.slice(0, 6)) {
            let place = candidate;
            if (place.place_id && (!place.photos || place.photos.length === 0)) {
                const details = await getDetails(place.place_id);
                statuses.push(`getDetails:${details.status}`);
                if (details.place) {
                    place = details.place;
                }
            }
            addPhotosFromPlace(place);
            if (photoMap.size >= 12) {
                return { photos: Array.from(photoMap.values()).slice(0, 12), status: statuses.join(' | ') };
            }
        }
    }

    return {
        photos: Array.from(photoMap.values()).slice(0, 12),
        status: statuses.length ? statuses.join(' | ') : 'ZERO_RESULTS'
    };
}

async function findStreetViewPosition(university) {
    const streetViewService = new google.maps.StreetViewService();
    const geocoder = new google.maps.Geocoder();

    const tryByLocation = (location, radius) => new Promise((resolve) => {
        streetViewService.getPanorama({ location, radius }, (data, status) => {
            if (status === 'OK' && data?.location?.latLng) {
                resolve(data.location.latLng);
                return;
            }
            resolve(null);
        });
    });

    const geocodeAddress = (address) => new Promise((resolve) => {
        geocoder.geocode({ address }, (results, status) => {
            if (status === 'OK' && results?.length) {
                resolve(results[0].geometry.location);
                return;
            }
            resolve(null);
        });
    });

    const nameQueries = [
        `${university.name}, ${university.country}`,
        `${university.name}, ${university.address}, ${university.country}`,
        `${university.name} university ${university.country}`
    ];

    const radii = [400, 800, 1400, 2200];

    for (const query of nameQueries) {
        const geocodedLocation = await geocodeAddress(query);
        if (!geocodedLocation) {
            continue;
        }
        for (const radius of radii) {
            const position = await tryByLocation(geocodedLocation, radius);
            if (position) {
                return position;
            }
        }
    }

    const base = {
        lat: parseFloat(university.latitude),
        lng: parseFloat(university.longitude)
    };

    for (const radius of radii) {
        const position = await tryByLocation(base, radius);
        if (position) {
            return position;
        }
    }

    return null;
}

window.findPlaceByUniversity = findPlaceByUniversity;
window.findStreetViewPosition = findStreetViewPosition;
