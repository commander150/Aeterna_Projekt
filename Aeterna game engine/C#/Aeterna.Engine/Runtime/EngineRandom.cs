using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;

namespace Aeterna.Engine.Runtime;

internal static class EngineRandom
{
    internal static void Shuffle<T>(
        IList<T> values,
        int matchSeed,
        string streamId,
        int shuffleSequence)
    {
        ArgumentNullException.ThrowIfNull(values);
        if (string.IsNullOrWhiteSpace(streamId))
        {
            throw new ArgumentException("Random stream ID is required.", nameof(streamId));
        }

        if (shuffleSequence < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(shuffleSequence));
        }

        var random = new DeterministicRandom(matchSeed, streamId, shuffleSequence);
        for (var index = values.Count - 1; index > 0; index -= 1)
        {
            var swapIndex = random.NextInt32(index + 1);
            (values[index], values[swapIndex]) = (values[swapIndex], values[index]);
        }
    }

    private sealed class DeterministicRandom
    {
        private readonly byte[] _streamKey;
        private ulong _blockSequence;

        internal DeterministicRandom(int matchSeed, string streamId, int shuffleSequence)
        {
            var material = Encoding.UTF8.GetBytes(
                $"aeterna-engine-random-v1\n{matchSeed}\n{shuffleSequence}\n{streamId}");
            _streamKey = SHA256.HashData(material);
        }

        internal int NextInt32(int exclusiveUpperBound)
        {
            if (exclusiveUpperBound <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(exclusiveUpperBound));
            }

            var bound = (uint)exclusiveUpperBound;
            var rejectionLimit = uint.MaxValue - uint.MaxValue % bound;
            while (true)
            {
                var candidate = NextUInt32();
                if (candidate < rejectionLimit)
                {
                    return (int)(candidate % bound);
                }
            }
        }

        private uint NextUInt32()
        {
            Span<byte> counter = stackalloc byte[sizeof(ulong)];
            BinaryPrimitives.WriteUInt64LittleEndian(counter, _blockSequence);
            _blockSequence += 1;
            using var hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
            hash.AppendData(_streamKey);
            hash.AppendData(counter);
            Span<byte> output = stackalloc byte[32];
            if (!hash.TryGetHashAndReset(output, out var bytesWritten) || bytesWritten != output.Length)
            {
                throw new InvalidOperationException("Deterministic random block generation failed.");
            }

            return BinaryPrimitives.ReadUInt32LittleEndian(output);
        }
    }
}
