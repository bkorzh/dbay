import argparse
import logging

from .server import SimServer


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dbay-sim",
        description="Virtual DBay hardware: UDP server mimicking the Teensy firmware.",
    )
    parser.add_argument("--host", default="0.0.0.0", help="address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8880, help="UDP port (default: 8880, same as the hardware)")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible ADC readings")
    parser.add_argument("-v", "--verbose", action="store_true", help="log every UDP exchange")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    server = SimServer(host=args.host, port=args.port, seed=args.seed)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
